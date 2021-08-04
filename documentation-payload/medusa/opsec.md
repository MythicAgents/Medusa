+++
title = "OPSEC"
chapter = false
weight = 10
pre = "<b>1. </b>"
+++

### Process Execution

- The `shell` command spawns a child process which is subject to command-line logging.
- The `shinject` command (for Windows only) uses the well-known CreateRemoteThread injection technique.
- The `load_dll` command (for Windows only) needs the DLL to respond with an integer value (and not exit the process) on completion.

### Agent payload

The build parameters offer an XOR+Base64 obfuscation option. Rather than outputting a more trivially-signaturable script that is clearly readable, Mythic will bundle the code and XOR+Base64 it with a random key. This is then decrypted, decoded and run with `exec()` to ultimately execute the agent.

With the function `load` available, as well as the potential utility of the `cryptography` library, you could reduce your payload size and capabilities for initial access (potentially using a python one-liner to achieve code execution). The agent can then be updated with additional functions as required.

An example of the XOR payload compared to the plaintext script can be seen below:

![XOR Payload](/agents/medusa/xor.png)
