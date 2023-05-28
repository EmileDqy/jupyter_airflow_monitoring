from notebook.utils import url_path_join
from .apihandlers import MessageHandler, set_message, get_message

__all__ = ['set_message', 'get_message']

def _jupyter_server_extension_paths():
    return [{
        "module": "jupyter_airflow_monitoring"
    }]

def _jupyter_nbextension_paths():
    return [{
        "section": "notebook",
        "dest": "jupyter_airflow_monitoring",
        "src": "static",
        "require": "jupyter_airflow_monitoring/main"
    }]

def load_jupyter_server_extension(nbapp):
    web_app = nbapp.web_app
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'], '/message')
    web_app.add_handlers(host_pattern, [(route_pattern, MessageHandler)])