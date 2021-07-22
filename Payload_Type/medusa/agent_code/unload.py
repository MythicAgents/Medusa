    def unload(self, task_id, command):
        delattr(medusa, command)
        cmd_list = [{"action": "remove", "cmd": command}]
        responses = [{ "task_id": task_id, "user_output": "Unloaded command: {}".format(command), "commands": cmd_list, "completed": True }]
        message = { "action": "post_response", "responses": responses }
        response_data = self.postMessageAndRetrieveResponse(message)
