+++
title = "ls"
chapter = false
weight = 100
hidden = false
+++

## Summary

Get attributes about a file and display it to the user via API calls. No need for quotes and relative paths are fine 

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500  

### Arguments

#### path

- Description: Path of file or folder on the current system to list   
- Required Value: True  
- Default Value: .  

## Usage

```
ls /path/to/file
```

## MITRE ATT&CK Mapping

- T1106  
- T1083  

## Detailed Summary
This command used python `os` library functions to get the contents of directories and metadata of files. 

Python 2.7:
```Python
    def ls(self, task_id, path, file_browser=False):
        if path == ".": file_path = self.current_directory
        else: file_path = path if path[0] == os.sep \
                else os.path.join(self.current_directory,path)
        file_details = os.stat(file_path)
        target_is_file = os.path.isfile(file_path)
        target_name = os.path.basename(file_path.rstrip(os.sep))
        file_browser = {
            "host": socket.gethostname(),
            "is_file": target_is_file,
            "permissions": {"octal": oct(file_details.st_mode)[-3:]},
            "name": target_name if target_name != "." \
                    else os.path.basename(self.current_directory.rstrip(os.sep)),            "parent_path": os.path.abspath(os.path.join(file_path, os.pardir)),
            "success": True,
            "access_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_details.st_atime)),
            "modify_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_details.st_mtime)),
            "size": file_details.st_size,
            "update_deleted": True,
        }
        files = []
        if not target_is_file:
            for entry in os.listdir(file_path):
                full_path = os.path.join(file_path, entry)
                file = {}
                file['name'] = entry 
                file['is_file'] = True if os.path.isfile(full_path) else False
                try:
                    file_details = os.stat(full_path)
                    file["permissions"] = { "octal": oct(file_details.st_mode)[-3:]}
                    file["access_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_details.st_atime))
                    file["modify_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_details.st_mtime))
                    file["size"] = file_details.st_size
                except OSError as e:
                    pass
                files.append(file)
        file_browser["files"] = files
        task = [task for task in self.taskings if task["task_id"] == task_id]
        task[0]["file_browser"] = file_browser
        return { "files": files }
```

Python 3.8

```Python
    def ls(self, task_id, path, file_browser=False):
        if path == ".": file_path = self.current_directory
        else: file_path = path if path[0] == os.sep \
                else os.path.join(self.current_directory,path)
        file_details = os.stat(file_path)
        target_is_file = os.path.isfile(file_path)
        target_name = os.path.basename(file_path.rstrip(os.sep))
        file_browser = {
            "host": socket.gethostname(),
            "is_file": target_is_file,
            "permissions": {"octal": oct(file_details.st_mode)[-3:]},
            "name": target_name if target_name != "." \
                    else os.path.basename(self.current_directory.rstrip(os.sep)),            "parent_path": os.path.abspath(os.path.join(file_path, os.pardir)),
            "success": True,
            "access_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_details.st_atime)),
            "modify_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_details.st_mtime)),
            "size": file_details.st_size,
            "update_deleted": True,
        }
        files = []
        if not target_is_file:
            with os.scandir(file_path) as entries:
                for entry in entries:
                    file = {}
                    file['name'] = entry.name
                    file['is_file'] = True if entry.is_file() else False
                    try:
                        file_details = os.stat(os.path.join(file_path, entry.name))
                        file["permissions"] = { "octal": oct(file_details.st_mode)[-3:]}
                        file["access_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_details.st_atime))
                        file["modify_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_details.st_mtime))
                        file["size"] = file_details.st_size
                    except OSError as e:
                        pass
                    files.append(file)  
        file_browser["files"] = files
        task = [task for task in self.taskings if task["task_id"] == task_id]
        task[0]["file_browser"] = file_browser
        return { "files": files }

```

This command helps populate the file browser, which is where all this data can be seen.
