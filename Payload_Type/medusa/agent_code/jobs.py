    def jobs(self, task_id):
        out = [t.name.split(":") for t in threading.enumerate() \
            if t.name != "MainThread" and "a2m" not in t.name \
            and "m2a" not in t.name and t.name != "jobs:{}".format(task_id) ]
        if len(out) > 0: return json.dumps({ "jobs": out })
        else: return "No long running jobs!"
