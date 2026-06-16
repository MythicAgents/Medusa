+++
title = "pty"
chapter = false
weight = 100
hidden = false
+++

## Summary

Open an interactive PTY session with the agent. This command supports three modes, allowing the operator to either spawn a fully interactive terminal for an external program or drop into a Python REPL with access to live agent state.

- Python Versions Supported: 2.7, 3.8
- Needs Admin: False
- Version: 2
- Author: @ajpc500

### Arguments

#### mode

- Description: The PTY session mode to use.
  - `spawn` (default): Spawns a program (e.g. `/bin/bash`) with a PTY and proxies interactive I/O to it.
  - `self`: Opens an in-process Python REPL with live agent state. Code executed here runs inside the running agent, so changes to agent state persist.
  - `fork`: Forks the agent and opens a Python REPL with a snapshotted copy of agent state and full PTY support. The forked child's config is wiped to prevent it from beaconing but in-memory loaded dependencies, for example, will propagate.
- Required Value: False
- Default Value: spawn

#### program_path

- Description: What program to spawn with a PTY (`spawn` mode only).
- Required Value: False
- Default Value: /bin/bash

## Usage

```
pty [/bin/bash]
pty -mode self
pty -mode fork
```

In `self` and `fork` modes the following locals are available within the REPL:

- `agent`: the running agent instance
- `config`: the agent configuration (live in `self` mode, snapshotted in `fork` mode)
- `cwd`: the agent's current working directory
- `modules`: the agent's loaded module repository
- `task_id`: the current task id (`self` mode only)

## MITRE ATT&CK Mapping

- T1059

## Detailed Summary

The `pty` command leverages Mythic's interactive tasking support (`task_response:interactive`) to provide a live terminal session.

- In `spawn` mode, a pseudo-terminal is created with `pty.openpty()` and the target program is launched via `subprocess.Popen`, with the slave end of the PTY wired to the process's stdin, stdout, and stderr. A select-based I/O loop proxies bytes between the operator and the process, and control sequences (e.g. Ctrl-C, Tab, arrow keys) are translated to their corresponding terminal byte sequences.
- In `self` mode, an in-process `code.InteractiveConsole` is driven by the interactive input queue, capturing stdout/stderr and streaming the results back to the operator. Because it runs inside the agent process, it has live access to and can mutate agent state.
- In `fork` mode, the agent calls `os.forkpty()` and the child snapshots its configuration before wiping the live config (to prevent the fork from beaconing), then drops into a `code.interact` REPL with full PTY support. The parent proxies PTY I/O to the operator.
