![Medusa](agent_icons/medusa.svg)

# Medusa

Medusa is a cross-platform agent written in Python 3.8. 

## Installation
To install Medusa, you'll need Mythic installed on a remote computer. You can find installation instructions for Mythic at the [Mythic project page](https://github.com/its-a-feature/Mythic/).

From the Mythic install root, run the command:

`./mythic-cli payload install github https://github.com/MythicAgents/Medusa.git`

Once installed, restart Mythic to build a new agent.

## Notable Features
- File browser compatibility with upload/download
- Windows injection example using CreateRemoteThread
- maOS TCC database parsing example
- Eval() of dynamic Python code
- Basic Authentication Proxy compatibility

## Commands Manual Quick Reference

The base agent and included commands all use built-in Python libraries, so do not need additional packages to function.

Command | Syntax | Description
------- | ------ | -----------
cat | `cat path/to/file` | Read and output file content.
cd | `cd [.. dir]` | Change working directory (`..` to go up one directory).
cp | `cp src_file_or_dir dst_file_or_dir` | Copy file or folder to destination.
cwd | `cwd` | Print working directory.
download | `download [path]` | Download a file from the target system.
exit | `exit` | Exit a callback.
env | `env` | Print environment variables.
eval | `eval [commands]` | Execute python code and return output.
exec | `exec [python code]` | Execute python code with exec().
ls | `ls [. path]` | List files and folders in `[path]` or use `.` for current working directory.
list_tcc | `list_tcc [path]` | List entries in macOS TCC database (requires full-disk access and Big Sur only atm).
mv | `mv src_file_or_dir dst_file_or_dir` | Move file or folder to destination.
rm | `rm file_or_dir` | Delete file or folder.
shell | `shell [command]` | Run a shell command which will spawn using subprocess.Popen(). Note that this will wait for command to complete so be careful not to block your agent.
shinject | `shinject` | Inject shellcode into target PID using CreateRemoteThread (Windows only - adapted from [here](https://gist.github.com/RobinDavid/9214020)).
sleep | `sleep [seconds] [jitter percentage]` | Set the callback interval of the agent in seconds.
upload | `upload` | Upload a file to a remote path on the machine.

## Supported C2 Profiles

Currently, only one C2 profile is available to use when creating a new Medusa agent: http (both with and without AES256 HMAC encryption).

### HTTP Profile

The HTTP profile calls back to the Mythic server over the basic, non-dynamic profile. GET requests for taskings, POST requests with responses.

## Thanks

- Browser scripts and agent code adapted from [@its_a_feature_](https://twitter.com/its_a_feature_) and [@djhohnstein](https://twitter.com/djhohnstein).
- Agent icon from [flaticon.com](https://www.flaticon.com)