+++
title = "rm"
chapter = false
weight = 100
hidden = false
+++

## Summary

Remove a file or directory, no quotes are necessary and relative paths are fine 

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500  

### Arguments

#### path

- Description: Path to file or folder to remove  
- Required Value: True  
- Default Value: None  

## Usage

```
rm ../path/to/file_or_folder
```

## MITRE ATT&CK Mapping

- T1106  
- T1107  

## Detailed Summary
Uses Python `os` library functions to remove the file or folder specified:
```Python
    def rm(self, task_id, path):
        import shutil
        file_path = path if path[0] == os.sep \
                else os.path.join(self.current_directory,path)
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)

```
