+++
title = "exit"
chapter = false
weight = 100
hidden = false
+++

## Summary

This exits the current Medusa agent. 

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500  

## Usage

```
exit
```


## Detailed Summary

The command executes this call:
```Python
    def exit(self, task_id):
        os._exit(0)
```

