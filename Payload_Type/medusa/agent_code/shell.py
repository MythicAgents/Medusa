    def shell(self, task_id, command):
        import subprocess
        process = subprocess.Popen(command, stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, cwd=self.current_directory, shell=True)
        stdout, stderr = process.communicate()
        out = stderr if stderr else stdout
        return out.decode()
