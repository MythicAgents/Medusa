+++
title = "cd"
chapter = false
weight = 100
hidden = false
+++

## Summary

Change the current working directory to another directory. No quotes are necessary and relative paths are fine 

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500

### Arguments

#### path

- Description: path to change directory to  
- Required Value: True  
- Default Value: None  

## Usage

### Without Popup Option
```
cd ../path/here
```

## MITRE ATT&CK Mapping

- T1083

## Detailed Summary
You can either type `cd` and get a popup to fill in the path, or provide the path on the command line. 

```Python
    def cd(self, task_id, path):
        if path == "..":
            self.current_directory = os.path.dirname(os.path.dirname(self.current_directory + os.sep))
        else:
            self.current_directory = path if path[0] == os.sep \
                else os.path.abspath(os.path.join(self.current_directory,path))

```
