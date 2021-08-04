+++
title = "shell"
chapter = false
weight = 100
hidden = false
+++

## Summary

This runs {command} in a terminal by leveraging the `subprocess` Python library.
     
- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500  

### Arguments

#### command

- Description: Command to run  
- Required Value: True  
- Default Value: None  

## Usage

```
shell {command}
```

## MITRE ATT&CK Mapping

- T1059  

## Detailed Summary

In the event that stderr has content, this will be returned by the function, providing the operator with details of issues encountered.

```Python
    def shell(self, task_id, command):
        import subprocess
        process = subprocess.Popen(command.split(),
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE,
                     cwd=self.current_directory)
        stdout, stderr = process.communicate()
        out = stderr if stderr else stdout
        return out.decode()

```
