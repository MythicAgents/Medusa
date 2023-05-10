    def unload_module(self, task_id, module_name):
        if module_name in self._meta_cache:
            finder = self._meta_cache.pop(module_name)
            sys.meta_path.remove(finder)
            self.moduleRepo.pop(module_name)
            return "{} module unloaded".format(module_name)
        else: return "{} not found in loaded modules".format(module_name)
