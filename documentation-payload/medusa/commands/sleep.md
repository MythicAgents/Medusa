+++
title = "sleep"
chapter = false
weight = 100
hidden = false
+++

## Summary

Modify the time between callbacks in seconds. 

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500  

### Arguments

#### jitter

- Description: Percentage of C2's interval to use as jitter   
- Required Value: False  
- Default Value: None  

#### seconds

- Description: Number of seconds between checkins   
- Required Value: False  
- Default Value: None  

## Usage
### Without Popup

```
sleep [seconds] [jitter]
```

## MITRE ATT&CK Mapping

- T1029  

## Detailed Summary

Internally modifies the sleep interval and sleep jitter percentages when doing callbacks:

```Python
    def sleep(self, task_id, seconds, jitter=-1):
        self.agent_config["Sleep"] = int(seconds)
        if jitter != -1:
            self.agent_config["Jitter"] = int(jitter)

```
