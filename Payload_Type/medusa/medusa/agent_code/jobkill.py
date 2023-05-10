    def jobkill(self, task_id, target_task_id):
        task = [task for task in self.taskings if task["task_id"] == target_task_id]
        task[0]["stopped"] = True
