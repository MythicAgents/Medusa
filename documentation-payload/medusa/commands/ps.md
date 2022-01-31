+++
title = "ps"
chapter = false
weight = 100
hidden = false
+++

## Summary

This uses the ctypes library to interface with Windows API to enumerate process IDs and return a limited (marginally better opsec) process list.

- Python Versions Supported: 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500  

## Usage

```
ps
```

## MITRE ATT&CK Mapping

- T1057  

## Detailed Summary
This function will only return PID, process name, architecture and binary path. Further details can be pulled back with `ps_full`.

```Python
    def ps(self, task_id):
        import sys, os.path, ctypes, ctypes.wintypes, re
        from ctypes import create_unicode_buffer, GetLastError

        def _check_bool(result, func, args):
            if not result:
                raise ctypes.WinError(ctypes.get_last_error())
            return args

        PULONG = ctypes.POINTER(ctypes.wintypes.ULONG)
        ULONG_PTR = ctypes.wintypes.LPVOID
        SIZE_T = ctypes.c_size_t
        NTSTATUS = ctypes.wintypes.LONG
        PVOID = ctypes.wintypes.LPVOID
        PROCESSINFOCLASS = ctypes.wintypes.ULONG

        Psapi = ctypes.WinDLL('Psapi.dll')
        EnumProcesses = Psapi.EnumProcesses
        EnumProcesses.restype = ctypes.wintypes.BOOL
        GetProcessImageFileName = Psapi.GetProcessImageFileNameA
        GetProcessImageFileName.restype = ctypes.wintypes.DWORD

        Kernel32 = ctypes.WinDLL('kernel32.dll')
        OpenProcess = Kernel32.OpenProcess
        OpenProcess.restype = ctypes.wintypes.HANDLE
        CloseHandle = Kernel32.CloseHandle
        CloseHandle.errcheck = _check_bool
        IsWow64Process = Kernel32.IsWow64Process

        PROCESS_QUERY_INFORMATION = 0x0400

        WIN32_PROCESS_TIMES_TICKS_PER_SECOND = 1e7

        MAX_PATH = 260
        PROCESS_TERMINATE = 0x0001
        PROCESS_QUERY_INFORMATION = 0x0400

        TOKEN_QUERY = 0x0008
        TOKEN_READ = 0x00020008
        TOKEN_IMPERSONATE = 0x00000004
        TOKEN_QUERY_SOURCE = 0x0010
        TOKEN_DUPLICATE = 0x0002
        TOKEN_ASSIGN_PRIMARY = 0x0001 

        ProcessBasicInformation   = 0
        ProcessDebugPort          = 7
        ProcessWow64Information   = 26
        ProcessImageFileName      = 27
        ProcessBreakOnTermination = 29

        STATUS_UNSUCCESSFUL         = NTSTATUS(0xC0000001)
        STATUS_INFO_LENGTH_MISMATCH = NTSTATUS(0xC0000004).value
        STATUS_INVALID_HANDLE       = NTSTATUS(0xC0000008).value
        STATUS_OBJECT_TYPE_MISMATCH = NTSTATUS(0xC0000024).value

        def query_dos_device(drive_letter):
            chars = 1024
            drive_letter = drive_letter
            p = create_unicode_buffer(chars)
            if 0 == Kernel32.QueryDosDeviceW(drive_letter, p, chars):
                pass
            return p.value

        def create_drive_mapping():
            mappings = {}
            for letter in (chr(l) for l in range(ord('C'), ord('Z')+1)):
                try:
                    letter = u'%s:' % letter
                    mapped = query_dos_device(letter)
                    mappings[mapped] = letter
                except WindowsError: pass
            return mappings

        mappings = create_drive_mapping()

        def normalise_binpath(path):
            match = re.match(r'(^\\Device\\[a-zA-Z0-9]+)(\\.*)?$', path)
            if not match:
                return f"Cannot convert {path} into a Win32 compatible path"
            if not match.group(1) in mappings:
                return None
            drive = mappings[match.group(1)]
            if not drive or not match.group(2):
                return drive
            return drive + match.group(2)

        processes = []

        count = 32
        while True:
            ProcessIds = (ctypes.wintypes.DWORD*count)()
            cb = ctypes.sizeof(ProcessIds)
            BytesReturned = ctypes.wintypes.DWORD()
            if EnumProcesses(ctypes.byref(ProcessIds), cb, ctypes.byref(BytesReturned)):
                if BytesReturned.value<cb:
                    break
                else:
                    count *= 2
            else:
                sys.exit("Call to EnumProcesses failed")

        for index in range(int(BytesReturned.value / ctypes.sizeof(ctypes.wintypes.DWORD))):
            process = {}
            process["process_id"] = ProcessId = ProcessIds[index]
            if ProcessId == 0: continue

            hProcess = OpenProcess(PROCESS_QUERY_INFORMATION, False, ProcessId)
            if hProcess:
                ImageFileName = (ctypes.c_char*MAX_PATH)()
                Is64Bit = ctypes.c_int32()
                IsWow64Process(hProcess, ctypes.byref(Is64Bit))
                arch = "x86" if Is64Bit.value else "x64"
                process["architecture"] = arch


                if GetProcessImageFileName(hProcess, ImageFileName, MAX_PATH)>0:
                    filename = os.path.basename(ImageFileName.value)
                    process["name"] = filename.decode()
                    process["bin_path"] = normalise_binpath(ImageFileName.value.decode())
                    
                CloseHandle(hProcess)
            processes.append(process)

        task = [task for task in self.taskings if task["task_id"] == task_id]
        task[0]["processes"] = processes
        return { "processes": processes }

```

This output is turned into a sortable table via a browserscript.