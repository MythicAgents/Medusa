+++
title = "jobs"
chapter = false
weight = 100
hidden = false
+++

## Summary

Lists the currently running jobs (aka long-running functions) for our agent.

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500

## Usage

```
jobs
```

## Detailed Summary

Lists the long-running functions running for our agent, this omits the main thread, the jobs function itself and any threads associated with the SOCKS proxy (outside of the main SOCKS thread, which we do include):

```Python
    def jobs(self, task_id):
        out = [t.name.split(":") for t in threading.enumerate() \
            if t.name != "MainThread" and "a2m" not in t.name \
            and "m2a" not in t.name and t.name != "jobs:{}".format(task_id) ]
        if len(out) > 0: return { "jobs": out }
        else: return "No long running jobs!"

```

