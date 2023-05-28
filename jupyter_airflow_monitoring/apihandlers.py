from notebook.base.handlers import IPythonHandler
import json
import os

def get_message():
    if os.path.exists("/tmp/cache_extension.txt"):
        with open("/tmp/cache_extension.txt", "r") as f:
            return json.load(f)
    else:
        return {"message": "", "title": "", "color": ""}

def set_message(message, title, color):
    with open("/tmp/cache_extension.txt", "w") as f:
        f.write(json.dumps({"message": message, "title": title, "color": color}))

class MessageHandler(IPythonHandler):
    def get(self):
        self.finish(get_message())

    def post(self):
        message = self.get_body_argument('message', '')
        title = self.get_body_argument('title', '')
        color = self.get_body_argument('color', '')
        set_message(message, title, color)
