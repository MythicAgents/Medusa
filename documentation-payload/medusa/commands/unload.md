+++
title = "unload"
chapter = false
weight = 100
hidden = false
+++

## Summary

Unload an existing capability from the agent. 
     
- Python Versions Supported: 2.7, 3.8     
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500  

### Arguments

#### function

- Description: function to unload
- Required Value: True  
- Default Value: None  

## Usage

```
unload function
```

## Detailed Summary
Note that this will only unload the function from the instantiation of the Medusa agent class, it won't remove it from any on-disk script that was executed. So consider using this in a `load` then `unload` scenario.

```Python
    def unload(self, task_id, command):
        delattr(medusa, command)
        cmd_list = [{"action": "remove", "cmd": command}]
        responses = [{ "task_id": task_id, "user_output": "Unloaded command: {}".format(command), "commands": cmd_list, "completed": True }]
        message = { "action": "post_response", "responses": responses }
        response_data = self.postMessageAndRetrieveResponse(message)

```