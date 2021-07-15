    def cat(self, task_id, path):
        file_path = path if path[0] == os.sep \
                else os.path.join(self.current_directory,path)
        
        with open(file_path, 'r') as f:
            content = f.readlines()
            return ''.join(content)
