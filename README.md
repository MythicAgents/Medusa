<p align="center">
  <img alt="Medusa Logo" src="agent_icons/medusa.svg" height="30%" width="30%">
</p>

# Medusa

Medusa is a cross-platform agent compatible with both Python 3.8 and Python 2.7.

## Installation
To install Medusa, you'll need Mythic installed on a remote computer. You can find installation instructions for Mythic at the [Mythic project page](https://github.com/its-a-feature/Mythic/).

From the Mythic install root, run the command:

`./mythic-cli payload install github https://github.com/MythicAgents/Medusa.git`

Once installed, restart Mythic to build a new agent.

## Notable Features
- File browser compatibility with upload/download
- Windows injection example using CreateRemoteThread
- maOS clipboard reader, screenshot grabber and TCC database parsing examples
- Eval() of dynamic Python code
- Basic Authentication Proxy compatibility

## Commands Manual Quick Reference

The base agent and included commands all use built-in Python libraries, so do not need additional packages to function. Agents will run the commands in threads, so long-running uploads or downloads won't block the main agent.

Command | Syntax | Description
------- | ------ | -----------
cat | `cat path/to/file` | Read and output file content.
cd | `cd [.. dir]` | Change working directory (`..` to go up one directory).
clipboard | `clipboard` | Output contents of clipboard (uses Objective-C API, as outlined by Cedric Owens [here](https://github.com/cedowens/MacC2/blob/main/client.py#L90). macOS only, Python 2.7 only).
cp | `cp src_file_or_dir dst_file_or_dir` | Copy file or folder to destination.
cwd | `cwd` | Print working directory.
download | `download [path]` | Download a file from the target system.
exit | `exit` | Exit a callback.
env | `env` | Print environment variables.
eval | `eval [commands]` | Execute python code and return output.
ls | `ls [. path]` | List files and folders in `[path]` or use `.` for current working directory.
list_tcc | `list_tcc [path]` | List entries in macOS TCC database (requires full-disk access and Big Sur only atm).
mv | `mv src_file_or_dir dst_file_or_dir` | Move file or folder to destination.
rm | `rm file_or_dir` | Delete file or folder.
screenshot | `screenshot` | Take a screenshot (uses Objective-C API, macOS only, Python 2.7 only).
shell | `shell [command]` | Run a shell command which will spawn using subprocess.Popen(). Note that this will wait for command to complete so be careful not to block your agent.
shinject | `shinject` | Inject shellcode into target PID using CreateRemoteThread (Windows only - adapted from [here](https://gist.github.com/RobinDavid/9214020)).
sleep | `sleep [seconds] [jitter percentage]` | Set the callback interval of the agent in seconds.
upload | `upload` | Upload a file to a remote path on the machine.

## Python Versions

Both versions of the Medusa agent use an AES256 HMAC implementation written with built-in libraries (adapted from [here](https://github.com/boppreh/aes)), removing the need for any additional dependencies beyond a standard Python install. As such the agent should operate across Windows, Linux and macOS hosts. It's worth mentioning that this crypto implementation does introduce some overhead when handling large files (screenshotting, downloads, etc.) but it's workable.

### Py2 vs Py3 Commands

Within the `Payload_Type/Medusa/agent_code` directory, you will see `base_agent` files with both `py2` and `py3` suffixes. Likewise, similar file extensions can be seen for individual function files too. 

These are read by the `builder.py` script to firstly select the right base Python version of the Medusa agent. `builder.py` will then include commands that are specific to the chosen python version. In the case where a command only has a `.py` extension, this will be used by default, with the assumption being that no alternative code is needed between the Py2 and Py3 versions.

## Supported C2 Profiles

Currently, only one C2 profile is available to use when creating a new Medusa agent: http (both with and without AES256 HMAC encryption).

### HTTP Profile

The HTTP profile calls back to the Mythic server over the basic, non-dynamic profile. GET requests for taskings, POST requests with responses.

## Thanks

- Browser scripts and agent code adapted from [@its_a_feature_](https://twitter.com/its_a_feature_) and [@djhohnstein](https://twitter.com/djhohnstein).
- [MacC2](https://github.com/cedowens/MacC2/) and [this](https://medium.com/red-teaming-with-a-blue-team-mentality/making-objective-c-calls-from-python-standard-libraries-550ed3a30a30) blog post from Cedric Owens
- The crypto wizardry found [here](https://github.com/boppreh/aes).
- Agent icon from [flaticon.com](https://www.flaticon.com)