from setuptools import setup, find_packages

setup(
    name="jupyter_airflow_monitoring",
    version="0.1",
    packages=find_packages(),
    data_files=[
        ("etc/jupyter/jupyter_notebook_config.d", ["jupyter_airflow_monitoring.json"]),
        ("share/jupyter/nbextensions/jupyter_airflow_monitoring", [
            "jupyter_airflow_monitoring/static/main.js", 
            "jupyter_airflow_monitoring/static/main.css"
        ]),
    ],
)
