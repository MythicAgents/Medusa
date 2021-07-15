    def ls(self, task_id, path, file_browser=False):
        if path == ".":
            file_path = self.current_directory
        else:
            file_path = path if path[0] == os.sep \
                else os.path.join(self.current_directory,path)
        file_details = os.stat(file_path)
        target_is_file = os.path.isfile(file_path)
        
        file_browser = {
            "host": self.getHostname(),
            "is_file": target_is_file,
            "permissions": {"octal": oct(file_details.st_mode)[-3:]},
            "name": os.path.basename(file_path.rstrip(os.sep)),
            "parent_path": os.path.abspath(os.path.join(file_path, os.pardir)),
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
                    file_details = os.stat(os.path.join(file_path, entry.name))
                    file = {}
                    file['name'] = entry.name
                    file['is_file'] = True if entry.is_file() else False
                    file["permissions"] = { "octal": oct(file_details.st_mode)[-3:]}
                    file["access_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_details.st_atime))
                    file["modify_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_details.st_mtime))
                    file["size"] = file_details.st_size
                    files.append(file)
        
        file_browser["files"] = files
        task = [task for task in self.taskings if task["task_id"] == task_id]
        task[0]["file_browser"] = file_browser

        return { "files": files }
