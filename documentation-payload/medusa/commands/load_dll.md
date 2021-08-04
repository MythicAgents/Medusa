+++
title = "load_dll"
chapter = false
weight = 100
hidden = false
+++

## Summary

Uses Python's `ctypes` library to load a DLL on disk and execute it with a given export function.

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500

### Arguments

#### path

- Description: path to DLL on target file system
- Required Value: True  
- Default Value: None  

#### export

- Description: exported function to execute
- Required Value: True  
- Default Value: None  


## Usage

```
load_dll path/to/dll function_exported
```

## Detailed Summary

Uses the `ctypes` library to execute a DLL with its supported function. This expects a DLL that returns an int value and doesn't exit the process upon completion (because that'll kill the agent too!):

```Python
    def load_dll(self, task_id, dllpath, dllexport):
        from ctypes import WinDLL
        dll_file_path = dllpath if dllpath[0] == os.sep \
                else os.path.join(self.current_directory,dllpath)
        loaded_dll = WinDLL(dll_file_path)
        eval("{}.{}()".format("loaded_dll",dllexport))
        return "[*] {} Loaded.".format(dllpath)

```

