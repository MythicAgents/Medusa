+++
title = "pip_freeze"
chapter = false
weight = 100
hidden = false
+++

## Summary

Prints the currently installed python packages on the target system

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500

## Usage

```
pip_freeze
```

## Detailed Summary

Attempts to list packages (ideally with version information) using a series of methods, based on availability:

```Python
    def pip_freeze(self, task_id):
        out=""
        try:
            import pkg_resources
            installed_packages = pkg_resources.working_set
            installed_packages_list = sorted(["%s==%s" % (i.key, i.version) for i in installed_packages])
            return "\n".join(installed_packages_list)
        except:
            out+="[*] pkg_resources module not installed.\n"

        try:
            from pip._internal.operations.freeze import freeze
            installed_packages_list = freeze(local_only=True)
            return "\n".join(installed_packages_list)
        except:
            out+="[*] pip module not installed.\n"

        try:
            import pkgutil
            installed_packages_list = [ a for _, a, _ in pkgutil.iter_modules()]
            return "\n".join(installed_packages_list)
        except:
            out+="[*] pkgutil module not installed.\n"

        return out+"[!] No modules available to list installed packages." 
```

