    def watch_dir(self, task_id, path, seconds):
        import hashlib
        known_files = {}
        def diffFolder(file_path, print_out=True):
            for root, dirs, files in os.walk(file_path):
                for dir in dirs:
                    full_dir_path = os.path.join(root, dir)
                    if full_dir_path not in known_files.keys():
                        if print_out: self.sendTaskOutputUpdate(task_id, "\n[*] New Directory: {}".format(full_dir_path)	)
                        known_files[full_dir_path] = ""

                for file in files:
                    full_file_path = os.path.join(root, file)
                    file_size = 0  
                    try: 
                        with open(full_file_path, "rb") as in_f:
                            file_data = in_f.read()
                            file_size = len(file_data)
                    except: continue

                    hash = hashlib.md5(file_data).hexdigest()

                    if full_file_path not in known_files.keys() and hash not in known_files.values():
                        if print_out: self.sendTaskOutputUpdate(task_id, "\n[*] New File: {} - {} bytes ({})".format(full_file_path, file_size, hash))
                        known_files[full_file_path] = hash
                    elif full_file_path in known_files.keys() and hash not in known_files.values():
                        if print_out: self.sendTaskOutputUpdate(task_id, "\n[*] File Updated: {} - {} bytes ({})".format(full_file_path, file_size, hash))
                        known_files[full_file_path] = hash
                    elif full_file_path not in known_files.keys() and hash in known_files.values():
                        orig_file = [f for f,h in known_files.items() if h == hash][0]
                        if os.path.exists(os.path.join(file_path, orig_file)):
                            if print_out: self.sendTaskOutputUpdate(task_id, "\n[*] Copied File: {}->{} - {} bytes ({})".format(orig_file, full_file_path, file_size, hash))
                        else:
                            if print_out: self.sendTaskOutputUpdate(task_id, "\n[*] Moved File: {}->{} - {} bytes ({})".format(orig_file, full_file_path, file_size, hash))
                            known_files.pop(orig_file)
                    known_files[full_file_path] = hash
            for file in list(known_files):
                if not os.path.isdir(os.path.dirname(file)):
                    for del_file in [f for f in list(known_files) if f.startswith(os.path.dirname(file))]:
                        obj_type = "Directory" if not known_files[del_file] else "File"
                        if file in list(known_files):
                            if print_out: self.sendTaskOutputUpdate(task_id, "\n[*] {} deleted: {} {}".format(obj_type, \
                                del_file, "({})".format(known_files[del_file]) if known_files[del_file] else ""))
                            known_files.pop(file)
                else:
                    if os.path.basename(file) not in os.listdir(os.path.dirname(file)):
                        obj_type = "Directory" if not known_files[file] else "File"
                        if print_out: self.sendTaskOutputUpdate(task_id, "\n[*] {} deleted: {} {}".format(obj_type, file, \
                            "({})".format(known_files[file]) if known_files[file] else ""))
                        known_files.pop(file)
    
        if path == ".": file_path = self.current_directory
        else: file_path = path if path[0] == os.sep \
                else os.path.join(self.current_directory,path)

        if not os.path.isdir(file_path):
            return "[!] Path must be a valid directory"
        elif not os.access(file_path, os.R_OK):
            return "[!] Path not accessible"
        else:
            self.sendTaskOutputUpdate(task_id, "[*] Starting directory watch for {}".format(path))
            diffFolder(file_path, False) 
            while(True):
                if [task for task in self.taskings if task["task_id"] == task_id][0]["stopped"]: return "Job stopped."
                if not os.path.exists(file_path):
                    return "[!] Root directory has been deleted."
                diffFolder(file_path)
                time.sleep(seconds)
