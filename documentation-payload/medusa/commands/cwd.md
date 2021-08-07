+++
title = "cwd"
chapter = false
weight = 100
hidden = false
+++

## Summary

Prints the current working directory for the agent 

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500

## Usage

```
cwd
```

## MITRE ATT&CK Mapping

- T1083  

## Detailed Summary

Prints the variable value used by Medusa to track current directory:

```Python
    def cwd(self, task_id):
        return self.current_directory
```

