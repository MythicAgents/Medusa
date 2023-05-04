    def rm(self, task_id, path):
        import shutil
        file_path = path if path[0] == os.sep \
                else os.path.join(self.current_directory,path)
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)
