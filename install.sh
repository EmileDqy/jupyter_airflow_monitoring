set -x #echo on

pip install --no-cache-dir -I -e .
jupyter nbextension install --py --symlink --sys-prefix jupyter_airflow_monitoring
jupyter nbextension enable jupyter_airflow_monitoring --py --sys-prefix
jupyter serverextension enable jupyter_airflow_monitoring --py 