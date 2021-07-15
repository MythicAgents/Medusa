    def shell(self, task_id, command):
        import subprocess
        process = subprocess.Popen(command.split(),
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE,
                     cwd=self.current_directory)
        stdout, stderr = process.communicate()
        out = stderr if stderr else stdout
        return out.decode()
