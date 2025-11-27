from datetime import datetime

class Logger:
    def __init__(self, path="data/logs.txt"):
        self.path = path

    def log(self, agent, message):
        with open(self.path, "a") as f:
            f.write(f"[{datetime.now()}] [{agent}] {message}\n")

    def metric(self, name, value):
        self.log("METRIC", f"{name} = {value}")
