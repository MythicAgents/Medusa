+++
title = "list_modules"
chapter = false
weight = 100
hidden = false
+++

## Summary

Lists the modules (Python libraries) that have been loaded into the Medusa agent.

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500

### Arguments

#### module_name

- Description: specific module to output a full file listing for
- Required Value: False  
- Default Value: ""  


## Usage

```
list_modules [module_name]
```

## Detailed Summary

This function will list the name of the modules that have been loaded into memory, and can provide a detailed file listing if a module name is passed to it:

```Python
    def list_modules(self, task_id, module_name=""):
        if module_name:
            if module_name in self.moduleRepo.keys():
                return "\n".join(self.moduleRepo[module_name].namelist())
            else: return "{} not found in loaded modules".format(module_name)
        else:
            return "\n".join(self.moduleRepo.keys())

```

