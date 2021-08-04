+++
title = "eval_code"
chapter = false
weight = 100
hidden = false
+++

## Summary

Send and interpret new Python code.

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500

### Arguments

#### code

- Description: code to execute
- Required Value: True  
- Default Value: None  

## Usage

```
eval_code {code to execute}
```

## Detailed Summary

Uses the `eval()` function to interpret a string containing arbitrary Python code:

```Python
    def eval_code(self, task_id, command):
        return eval(command)

```

