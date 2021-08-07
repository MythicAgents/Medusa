+++
title = "env"
chapter = false
weight = 100
hidden = false
+++

## Summary

Prints the environment variables for the current process

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500

## Usage

```
env
```

## Detailed Summary

Lists the contents of the `os.environ` list:

```Python
    def env(self, task_id):
        return "\n".join(["{}: {}".format(x, os.environ[x]) for x in os.environ])
 
```

