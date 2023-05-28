import numpy as np
import pandas as pd
from typing import Dict, List
from airflow.models.baseoperator import BaseOperator
from airflow import DAG
from airflow.models.dagrun import DagRun
from airflow.models import DagBag
import pytz
from datetime import datetime
from jupyter_airflow_monitoring.apihandlers import set_message
from pretty_html_table import build_table

pd.options.plotting.backend = "plotly"

class InvalidJsonException(Exception): pass
class AirflowCliNotFoundException(Exception): pass
class AirflowCliException(Exception): pass
class InvalidDtypeException(Exception): pass

class DagsMonitoringOperator(BaseOperator):
    ui_color = "#ff0000"
    ui_fgcolor = "#000000"
    custom_operator_name = "DagsListenerOperator"
    DEFAULT_SEVERITY_COLORS_MAPPING = {
        3: "#FFDD00",
        2: "#FF9900",
        1: "#FF0000"
    }

    def __init__(self, monitored_tags_severity: Dict[str, int], severity_colors_mapping=DEFAULT_SEVERITY_COLORS_MAPPING, **kwargs) -> None:
        super().__init__(**kwargs) #hello
        self.log.info("Loading the dag bag...")
        self.monitored_tags_severity = monitored_tags_severity
        self.severity_colors_mapping = severity_colors_mapping
        self.dags = None

    def load_dags_list(self):
        self.dags = [{"dag_id": v.dag_id, "filepath": v.filepath, "paused": v.is_paused, "tags": v.tags} for v in self.dagbag.dags.values()]

    def get_active_dags(self):
        return list(filter(lambda x: x["paused"] == False, self.dags))

    def execute(self, context):
        self.log.info("Monitoring tags: " + ", ".join(list(self.monitored_tags_severity.keys())))
        self.dagbag = DagBag()

        self.log.info("Running...")
        self.load_dags_list()
        dags = self.get_active_dags()
        self.log.info(f"{len(dags)} dags...")

        def get_dag_runs_since_last_checked(dag_id: str) -> List[DagRun]:
            start = pytz.utc.localize(datetime(1970, 1, 1, 1, 1, 1))
            now = pytz.utc.localize(datetime.now())
            
            try:
                return DAG(dag_id).get_dagruns_between(start_date=start, end_date=now)
            except Exception as e:
                self.log.info(f"Exception while getting the last run of dag {dag_id}:", e)
                return []
        
        # Get the search history
        dags_data = []
        for dag in dags:
            # Filter for tracked dags
            if not any([i in self.monitored_tags_severity for i in dag["tags"]]):
                continue

            for i in get_dag_runs_since_last_checked(dag["dag_id"]):
                dag_run_metadata = {
                    "dag_id": i.dag_id, 
                    "dag_hash": i.dag_hash, 
                    "id": i.id, 
                    "run_id": i.run_id, 
                    "queued_at": i.queued_at.isoformat(), 
                    "execution_date": i.execution_date.isoformat(), 
                    "start_date": i.start_date.isoformat() if i.start_date else np.NaN, 
                    "end_date": i.end_date.isoformat() if i.end_date else np.NaN, 
                    "state": i.get_state(),
                    "is_backfill": i.is_backfill
                }
                dag_run_metadata.update(dag)
                dags_data.append(dag_run_metadata)

        # make decisions : df (the datetime objects are conserved)
        messages = {}
        
        df_dag_rungs_history = pd.DataFrame.from_records(dags_data)
        df_dag_rungs_history.drop_duplicates(
            inplace=True, 
            subset=["dag_id", "dag_hash", "id", "run_id", "queued_at", "execution_date", "start_date", "end_date", "state", "is_backfill"]
        )
        if df_dag_rungs_history.empty:
            set_message(message= "", title="", color="#FFFFFF")
            return None

        datetime_cols = ["queued_at","execution_date","start_date","end_date"]
        for col in datetime_cols:
            try:
                df_dag_rungs_history[col] = pd.to_datetime(df_dag_rungs_history[col])
            except:
                pass

        global_severity = 3
        self.log.info(df_dag_rungs_history.info())
        for dag_id, dag_runs in df_dag_rungs_history.groupby("dag_id"):
            dag_runs = dag_runs.set_index("queued_at")
            dag_runs.sort_index(inplace=True)
            
            # If the last run (or the last couple of runs) failed, we compute the rest
            if dag_runs["state"].iloc[-1] != "failed":
                continue
            
            dag_runs['state_block'] = (dag_runs['state'] != dag_runs['state'].shift()).cumsum()

            # Get the last failed DAG Run and its group of failed runs in a row
            df_state_failed = dag_runs[dag_runs['state'] == "failed"]

            last_value_block_id = df_state_failed['state_block'].iloc[-1]
            last_failed_state_block = df_state_failed[df_state_failed['state_block'] == last_value_block_id]
            
            severity = min([self.monitored_tags_severity.get(i, 3) for i in last_failed_state_block["tags"].explode().unique()])
            if severity < global_severity:
                global_severity = severity
            message = f"{repr(dag_id)} failed {len(last_failed_state_block)} time{'s in a row' if len(last_failed_state_block) > 1 else ''}. Was last queued at {df_state_failed.iloc[-1].name}"
            messages[dag_id] = {'message': message, 'severity': severity, "dag_id": dag_id}

        if messages:
            self.log.warning("\n".join(messages))
            messages = dict(sorted(messages.items(), key=lambda x:x[1]["severity"])) # Sort by priority

            df_dag_rungs_history = df_dag_rungs_history[["state"] + [i for i in df_dag_rungs_history.columns if i != "state"]]

            html_message  = "<h4>Information</h4>"
            html_message += "<br>".join([f"<p>[<b>severity {i['severity']}</b>] {i['message']}</p>" for i in messages.values()])
            html_message += "<hr>"
            html_message += "<h4>Last 10 failed runs</h4>"
            html_message += build_table(df_dag_rungs_history[df_dag_rungs_history.state == "failed"].sort_values("queued_at", ascending=False).head(10)[["dag_id", "queued_at", "tags"]], "orange_light", width="500px", font_size="small")
            set_message(message= html_message, title=f"{len([i['message'] for i in messages.values()])} failed: {', '.join([repr(k) + ' (severity ' + str(v['severity']) + ')' for k,v in messages.items()])}", color=self.severity_colors_mapping[global_severity])
        else:
            self.log.warning("Everything is good.")
            set_message(message= "", title="", color="#FFFFFF")

        return None