    def env(self, task_id):
        return "\n".join(["{}: {}".format(x, os.environ[x]) for x in os.environ])
 