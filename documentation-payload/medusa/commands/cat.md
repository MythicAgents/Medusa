+++
title = "cat"
chapter = false
weight = 100
hidden = false
+++

## Summary

Outputs the string content of a given file. No need for quotes and relative paths are fine.

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500

### Arguments

#### path_to_read

- Description: path to file we're going to read from
- Required Value: True  
- Default Value: None  

## Usage

```
cat /path/to/file
```

## MITRE ATT&CK Mapping

- T1005  

## Detailed Summary

Prints the contents of a file on the target system:

```Python
    def cat(self, task_id, path):
        file_path = path if path[0] == os.sep \
                else os.path.join(self.current_directory,path)
        
        with open(file_path, 'r') as f:
            content = f.readlines()
            return ''.join(content)

```

