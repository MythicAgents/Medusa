+++
title = "list_apps"
chapter = false
weight = 100
hidden = false
+++

## Summary

This uses NSApplication.RunningApplications API to get information about running applications.

- Python Versions Supported: 2.7
- Needs Admin: False  
- Version: 1  
- Author: @ajpc500  

## Usage

```
list_apps
```

## MITRE ATT&CK Mapping

- T1057  

## Detailed Summary
This is different than executing `ps` in a terminal since this only reports back running applications, not _all_ processes running on a system.

```Python
    def list_apps(self, task_id):
        from Cocoa import NSWorkspace
        app_json = []
        apps = NSWorkspace.sharedWorkspace().runningApplications()
        for app in apps:
            try:
                app_data = { "pid": str(app.processIdentifier()), "name": str(app.localizedName()), "exec_url": str(app.executableURL()) }
                app_json.append(app_data)
            except: pass
        return { "apps": app_json }

```

This output is turned into a sortable table via a browserscript.

