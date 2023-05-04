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
            "name": target_name if target_name not in [".", "" ] \
                    else os.path.basename(self.current_directory.rstrip(os.sep)),        
            "parent_path": os.path.abspath(os.path.join(file_path, os.pardir)),
            "success": True,
            "access_time": int(file_details.st_atime * 1000),
            "modify_time": int(file_details.st_mtime * 1000),
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
                        file["access_time"] = int(file_details.st_atime * 1000)
                        file["modify_time"] = int(file_details.st_mtime * 1000)
                        file["size"] = file_details.st_size
                    except OSError as e:
                        pass
                    files.append(file)  
        file_browser["files"] = files
        task = [task for task in self.taskings if task["task_id"] == task_id]
        task[0]["file_browser"] = file_browser
        output = { "files": files, "parent_path": os.path.abspath(os.path.join(file_path, os.pardir)), "name":  target_name if target_name not in  [".", ""] \
                    else os.path.basename(self.current_directory.rstrip(os.sep))  }
        return json.dumps(output)
