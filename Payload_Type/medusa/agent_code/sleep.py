    def sleep(self, task_id, seconds, jitter=-1):
        self.agent_config["Sleep"] = int(seconds)
        if jitter != -1:
            self.agent_config["Jitter"] = int(jitter)
