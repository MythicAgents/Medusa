    def list_modules(self, task_id, module_name=""):
        if module_name:
            if module_name in self.moduleRepo.keys():
                return "\n".join(self.moduleRepo[module_name].namelist())
            else: return "{} not found in loaded modules".format(module_name)
        else:
            return "\n".join(self.moduleRepo.keys())
