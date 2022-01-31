+++
title = "kill"
chapter = false
weight = 100
hidden = false
+++

## Summary

This uses the ctypes library to interface with Windows API to terminate a process with a specified PID.

- Python Versions Supported: 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500  

## Usage

```
kill process_id
```


## Detailed Summary
This function takes a given PID and attempts to open a process handle and terminate it.

```Python
    def kill(self, task_id, process_id):
        import ctypes, ctypes.wintypes
        from ctypes import GetLastError

        NTSTATUS = ctypes.wintypes.LONG

        def _check_bool(result, func, args):
            if not result:
                raise ctypes.WinError(ctypes.get_last_error())
            return args
        
        Kernel32 = ctypes.WinDLL('kernel32.dll')
        OpenProcess = Kernel32.OpenProcess
        OpenProcess.restype = ctypes.wintypes.HANDLE
        CloseHandle = Kernel32.CloseHandle
        CloseHandle.errcheck = _check_bool
        TerminateProcess = Kernel32.TerminateProcess
        TerminateProcess.restype = ctypes.wintypes.BOOL

        PROCESS_TERMINATE = 0x0001
        PROCESS_QUERY_INFORMATION = 0x0400
        
        try:
            hProcess = OpenProcess(PROCESS_TERMINATE | PROCESS_QUERY_INFORMATION, False, process_id)
            if hProcess:
                TerminateProcess(hProcess, 1)
                CloseHandle(hProcess)    
        except Exception as e:
            return e

```