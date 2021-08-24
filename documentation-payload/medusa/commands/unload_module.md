+++
title = "unload_module"
chapter = false
weight = 100
hidden = false
+++

## Summary

Unloads a module that is currently loaded in-memory.

>**NOTE** If the module has already been imported in a custom script, it will remain importable in subsequent scripts.


- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500

### Arguments

#### module_name

- Description: the name of the module to unload, e.g. 'dns'
- Required Value: True  
- Default Value: None  

## Usage

```
unload_module module_name
```

## Detailed Summary

This function removes the custom finder added to the `meta_path`. It also removes the zip file from the agent dictionary:

```Python
    def unload_module(self, task_id, module_name):
        if module_name in self._meta_cache:
            finder = self._meta_cache.pop(module_name)
            sys.meta_path.remove(finder)
            self.moduleRepo.pop(module_name)
            return "{} module unloaded".format(module_name)
        else: return "{} not found in loaded modules".format(module_name)

```