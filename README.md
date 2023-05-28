# Jupyter Airflow Monitoring
![Demo Gif](./images/demo.gif)

The Jupyter Airflow Monitoring project is a solution designed to monitor Apache Airflow's DAGs directly from your Jupyter environment. Its primary objective is to monitor only the DAGs you are interested in, and do it in a non-invasive way to avoid adding unnecessary friction. This project is particularly valuable for data scientists and developers who frequently work with Jupyter notebooks and want to keep an eye on their Airflow workflows.

## Why Jupyter Airflow Monitoring?

While working with Airflow, it can be somewhat challenging to monitor the status of your DAGs, especially when you only need to track specific DAGs. This project proposes a solution for this problem by providing a way to specify tags for the DAGs you want to monitor and their corresponding severity levels if a DAG with the specified tag fails. This feature allows for customized and focused monitoring of your Airflow workflows. 

## Installation

> :warning: **WARNING**: please note that the current version of this project is limited to systems where both Airflow and Jupyter are running on the same host. *Additionally*, it is only compatible with Airflow standalone installations. It is theoretically possible to install it on a dockerized airflow with a shared volume though but I didn't try yet (you would need to install the module on both the host and the airflow image). 
__I plan on adding more flexibility/features in the future.__

To install this project, there are two methods:

### Method 1
1. Clone the repo
```
git clone https://github.com/EmileDqy/jupyter_airflow_monitoring.git
cd jupyter_airflow_monitoring
```

2. Install using the `install.sh` script
```
./install.sh
```

### Method 2
1. Clone the repo
```
git clone https://github.com/EmileDqy/jupyter_airflow_monitoring.git
cd jupyter_airflow_monitoring
```

2. Install using pip:
```
pip install .
```

3. Use the Jupyter CLI to enable the extension:

```
jupyter nbextension install --py --symlink --sys-prefix jupyter_airflow_monitoring
jupyter nbextension enable jupyter_airflow_monitoring --py --sys-prefix
jupyter serverextension enable jupyter_airflow_monitoring --py 
```

For your convenience, we also provide an `install.sh` script that will carry out the steps mentioned above.

## Usage

Once the extension is installed, an operator `DagsMonitoringOperator` is made available which can be used to create a DAG. This DAG is then scheduled to run at your preferred frequency (e.g., hourly) to monitor your DAGs.

Here is an example:

```python
# Import the new Operator
from jupyter_airflow_monitoring.operator import DagsMonitoringOperator
from airflow import models
import pendulum

with models.DAG(
    dag_id="monitoring",
    schedule="@hourly", # Check every hour
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    catchup=False,
) as dag:
    task = DagsMonitoringOperator(
        task_id="monitoring", 
        monitored_tags_severity={
            "example": 1, # All dags with tag 'example' will have severity=1 (red) when they fail
            "something": 2 # Severity = 2 (orange)
            "example_ui": 3 # Severity = 3 (yellow)
        }
    )
    task
```

In this example, the DAG with the id `monitoring2` is scheduled to run hourly, starting from January 1, 2021. The `DagsListenerOperator` monitors the DAGs with the tags "example" and "example_ui", with corresponding severity levels of 1 and 3.

## Python API

In addition to the operator, the project also exposes a Python API that allows setting and getting messages related to the monitored DAGs. This can be useful for more fine-grained control or custom integrations. Here is how you can use it:

```python
from jupyter_airflow_monitoring import set_message, get_message

# Set a message
set_message("DAG Failed", "MyDAG", "#FF0000")

# Get the message
message = get_message()
```

## Screenshots

![Demo Gif](./images/demo.gif)

##### When a DAG with a severity 1 fails:
Default view:
![Mouse not Hovering](./images/nohover.png)

On mouse hover:
![Mouse Hovering](./images/hover.png)

On click:
![Modal](./images/modal.png)


## Contributing

Contributions to this project are welcome! Please feel free to submit a Pull Request or open an issue on GitHub if you encounter any problems or have suggestions for improvements. Please note that I'm fairly new to jupyter extension development.

## TODOs

1) Add support for windows based systems
2) Add support for dockerized airflow
3) Add option to use a connexion so that the airflow operator can communicate with the jupyter server (airflow on a different system than the jupyter server)
4) Add monitoring by dag_id
5) Add monitoring automatic: run when a tracked DAG finished

## License

This project is licensed under the terms of the Apache-2.0 license.

I hope that this project helps improve your workflow and productivity when working with
