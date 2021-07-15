    def cd(self, task_id, path):
        if path == "..":
            self.current_directory = os.path.dirname(os.path.dirname(self.current_directory + os.sep))
        else:
            self.current_directory = path if path[0] == os.sep \
                else os.path.abspath(os.path.join(self.current_directory,path))
