<p align="center">
  <img alt="Medusa Logo" src="agent_icons/medusa.svg" height="30%" width="30%">
</p>

# Medusa

Medusa is a cross-platform agent compatible with both Python 3.8 and Python 2.7.

## Installation
To install Medusa, you'll need Mythic installed on a remote computer. You can find installation instructions for Mythic at the [Mythic project page](https://github.com/its-a-feature/Mythic/).

From the Mythic install root, run the command:

`./mythic-cli install github https://github.com/MythicAgents/Medusa.git`

Once installed, restart Mythic to build a new agent.

## Notable Features
- Dynamic loading/unloading of agent functions to limit exposure of agent capabilities on-disk.
- Loading of Python modules in-memory for use in custom scripts.
- Cross-platform SOCKS5 proxy
- maOS clipboard reader, screenshot grabber and TCC database parsing examples
- File browser compatibility with upload/download
- Eval() of dynamic Python code
- Basic Authentication Proxy compatibility

## Commands Manual Quick Reference

The base agent and included commands all use built-in Python libraries, so do not need additional packages to function. Agents will run the commands in threads, so long-running uploads or downloads won't block the main agent.

### General Commands

Command | Syntax | Description
------- | ------ | -----------
cat | `cat path/to/file` | Read and output file content.
cd | `cd [.. dir]` | Change working directory (`..` to go up one directory).
cp | `cp src_file_or_dir dst_file_or_dir` | Copy file or folder to destination.
cwd | `cwd` | Print working directory.
download | `download [path]` | Download a file from the target system.
exit | `exit` | Exit a callback.
env | `env` | Print environment variables.
eval_code | `eval_code [commands]` | Execute python code and return output.
jobkill | `jobkill [task id]` | Send stop signal to long running task.
jobs | `jobs` | List long-running tasks, such as downloads.
list_modules | `list_modules [module_name]` | Lists in-memory modules or the full file listing for a specific module.
load | `load command` | Load a new capability into an agent.
load_module | `load_module` | Load a zipped Python module into memory (adapted from [here](https://github.com/sulinx/remote_importer) and [here](https://github.com/EmpireProject/EmPyre/blob/master/data/agent/agent.py#L464)).
load_script | `load_script` | Load and execute a Python script through the agent.
ls | `ls [. path]` | List files and folders in `[path]` or use `.` for current working directory.
mv | `mv src_file_or_dir dst_file_or_dir` | Move file or folder to destination.
pip_freeze | `pip_freeze` | Programmatically list installed packages on system.
rm | `rm file_or_dir` | Delete file or folder.
shell | `shell [command]` | Run a shell command which will spawn using subprocess.Popen(). Note that this will wait for command to complete so be careful not to block your agent.
socks | `socks start/stop [port]` | Start/stop SOCKS5 proxy through Medusa agent. 
sleep | `sleep [seconds] [jitter percentage]` | Set the callback interval of the agent in seconds.
unload | `unload command` | Unload an existing capability from an agent.
unload_module | `unload_module module_name` | Unload a Python module previously loaded into memory.
upload | `upload` | Upload a file to a remote path on the machine.
watch_dir | `watch_dir path seconds` | Watch for changes in target directory, polling for changes at a specified rate.


### macOS Commands 

Command | Syntax | Description
------- | ------ | -----------
clipboard | `clipboard` | Output contents of clipboard (uses Objective-C API, as outlined by Cedric Owens [here](https://github.com/cedowens/MacC2/blob/main/client.py#L90). macOS only, Python 2.7 only).
list_apps | `list_apps` | List macOS applications (Python 2.7 only, macOS only).
list_tcc | `list_tcc [path]` | List entries in macOS TCC database (requires full-disk access and Big Sur only atm).
screenshot | `screenshot` | Take a screenshot (uses Objective-C API, macOS only, Python 2.7 only).
spawn_jxa | `spawn_jxa` | Spawn an `osascript` process and pipe Javascript content to it.
vscode_list_recent | `vscode_list_recent [state_db]` | Lists files and folders recently opened with VSCode.
vscode_open_edits | `vscode_open_edits [backup_dir_path]` | Lists unsaved changes made to files in VSCode.
vscode_watch_edits | `vscode_watch_edits [path to remote dir] [poll_interval]` | Poll the VSCode backups directory at a given interval for unsaved edits.

### Windows Commands

Command | Syntax | Description
------- | ------ | -----------
shinject | `shinject` | Inject shellcode into target PID using CreateRemoteThread (Windows only - adapted from [here](https://gist.github.com/RobinDavid/9214020)).
load_dll | `load_dll dll_path dll_export` | Load an on-disk DLL and execute an exported function (NOTE: This DLL must return an int value on completion, an msfvenom-created DLL, for example, will kill your agent upon completion).
list_dlls | `list_dlls [pid]` | Read process memory (PEB) of local or target process to fetch list of loaded DLLs (Python 3 only)
ps | `ps` | Get limited process information, e.g. PID, process names, architecture and binary paths (Python 3 only)
ps_full | `ps_full` | Get full process information, including PPID, integrity level and command line (Python 3 only)
kill | `kill` | Terminate a process by process ID (Python 3 only)


## Python Versions

Both versions of the Medusa agent use an AES256 HMAC implementation written with built-in libraries (adapted from [here](https://github.com/boppreh/aes)), removing the need for any additional dependencies beyond a standard Python install. As such the agent should operate across Windows, Linux and macOS hosts. It's worth mentioning that this crypto implementation does introduce some overhead when handling large files (screenshotting, downloads, etc.) but it's workable.

### Py2 vs Py3 Commands

Within the `Payload_Type/Medusa/agent_code` directory, you will see `base_agent` files with both `py2` and `py3` suffixes. Likewise, similar file extensions can be seen for individual function files too. 

These are read by the `builder.py` script to firstly select the right base Python version of the Medusa agent. `builder.py` will then include commands that are specific to the chosen python version. In the case where a command only has a `.py` extension, this will be used by default, with the assumption being that no alternative code is needed between the Py2 and Py3 versions.

## Threaded Jobs

Medusa uses basic threading for job execution. Where jobs are potentially long-running, they can be implemented with a 'stop check' to respond to a signal from the `jobkill` task. This can be implemented with a code snippet similar to that shown below:
```
if [task for task in self.taskings if task["task_id"] == task_id][0]["stopped"]:
  # Some job-specific tidy up
  return "Job stopped."
```
This handler can be seen implemented within the `download`, `upload`, `watch_dir` and `screenshot` commands.

Additionally, if the long-running job is expected to provide continuous output, the `sendTaskOutputUpdate` function - included in the base agent - can be used to update Mythic prior to the task completion. A dummy function that provides continuous output and can be `jobkill`'d can be seen below.

```
def dummyFunction(self, task_id):
  while(True):
      # Check if we've got a stop signal.
      if [task for task in self.taskings if task["task_id"] == task_id][0]["stopped"]: return "Job stopped."
      
      # Send output back to Mythic
      self.sendTaskOutputUpdate(task_id, "We're still running")

      time.sleep(10)
```

## Supported C2 Profiles

Currently, only one C2 profile is available to use when creating a new Medusa agent: http (both with and without AES256 HMAC encryption).

### HTTP Profile

The HTTP profile calls back to the Mythic server over the basic, non-dynamic profile. GET requests for taskings, POST requests with responses.

## Thanks

- Browser scripts and agent code adapted from [@its_a_feature_](https://twitter.com/its_a_feature_) and [@djhohnstein](https://twitter.com/djhohnstein).
- [MacC2](https://github.com/cedowens/MacC2/) and [this](https://medium.com/red-teaming-with-a-blue-team-mentality/making-objective-c-calls-from-python-standard-libraries-550ed3a30a30) blog post from Cedric Owens
- [EmPyre](https://github.com/EmpireProject/EmPyre/) and [this](https://www.xorrior.com/In-Memory-Python-Imports/) blog post from Chris Ross.
- The crypto wizardry found [here](https://github.com/boppreh/aes).
- Agent icon from [flaticon.com](https://www.flaticon.com)