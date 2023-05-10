    def mv(self, task_id, source, destination):
        import shutil
        source_path = source if source[0] == os.sep \
                else os.path.join(self.current_directory,source)
        dest_path = destination if destination[0] == os.sep \
                else os.path.join(self.current_directory,destination)
        shutil.move(source_path, dest_path)
