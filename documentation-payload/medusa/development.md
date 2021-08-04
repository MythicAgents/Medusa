+++
title = "Development"
chapter = false
weight = 20
pre = "<b>3. </b>"
+++

## Adding Commands

Commands are located in `Payload_Types/medusa/agent_code/`. Notably, there are three file extensions you might encounter. A given command can be included solely as a `.py`, if it could be used in a Python 2.7 or 3.8 script with no modification. Where changes are required, be that due to syntax, libraries, etc. a `.py2` and/or `.py3` file is used. These are looked up at payload build-time to ensure the correct function code is included.

In addition to the `.py*` files above, the function definitions found in `Payload_Types/medusa/mythic/agent_functions/` include an attribute that specifies which versions of Python a given function is compatible with (as well as which OSs). Using the `download` function as an example:

```Python
class DownloadCommand(CommandBase):
    cmd = "download"
    ...
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[ SupportedOS.MacOS, SupportedOS.Windows, SupportedOS.Linux ],
    )
```

Here we can see that the download function is supported by all OSs and both versions of Python.

When it comes to dynamic function loading, this `supported_python_versions` attribute is used by the `load` command to ensure only compatible functions are presented in the UI for loading into a live agent (see below).

```Python
async def get_commands(self, callback: dict) -> [str]:
	resp = await MythicRPC().execute("get_callback_commands", callback_id=callback["id"])
	return [ cmd["cmd"] for cmd in resp.response if callback["build_parameters"]["python_version"] in cmd["attributes"]["supported_python_versions"]]

```

All commands follow the general format below (where `command_name` is the name of the command you'd type in the U)):

```Python
    def command_name(self, task_id, input):
		doThing(input)
		return "output for mythic"

```
 
It's worth noting that the `task_id` argument is always passed in to a function. This allows any function to look up its own task in the Medusa agent's `self.taskings` variable. Amongst other things, this allows it to check if its been set to a 'stopped' state by the main thread and should therefore cease execution.

Similarly, as all functions are read and concatenated at build-time, we need to respect tabulation to ensure the resulting Python script actually runs. As a result, every function is 4-spaces indented.


### Available Components within Commands

Inside of commands, you get access to certain extra functions and information that's part of the agent overall.

Firstly, as mentioned above, we have the `task_id` value. When implementing long-running functions using while-loops for example, we can include a check to make sure we're good to keep going. This can be implemented as below:

```Python
	def long_running_task(self, task_id):
		while True:
			if [task for task in self.taskings if task["task_id"] == task_id][0]["stopped"]: return "Job stopped."
			# do some cool stuff
```

Similarly, where our function has mid-execution output to stream back to Mythic, there is an included `sendTaskOutputUpdate()` function which can be used to send updates. It's worth noting that this function is _currently_ not tied into the main thread responses, and will send data back to Mythic immediately upon execution.

This function can be executed within a function as below:

```Python
	def streamed_output(self, task_id):
		# Send output back to Mythic
		self.sendTaskOutputUpdate(self, task_id, "We're running")
		time.sleep(1)
		self.sendTaskOutputUpdate(self, task_id, "We slept a little")
		time.sleep(10000)
		self.sendTaskOutputUpdate(self, task_id, "what year is it?!?")
```


## Modifying base agent behavior

The base agent templates can be found at `Payload_Types/medusa/agent_code/base_agent/`. Just as with functions, there are `.py2` and `.py3` files included for the two supported Python versions.

Medusa supports use of either the non-default `cryptography` library (installed on macOS, but not ubiquitous elsewhere) or a manual crypto implementation using built-in libraries for its encrypted communications. For this reason, within the `base_agent/` directory, you'll see a pair of `crypto_lib` python files and a pair of `manual_crypto` files. As you can probably guess, this allows an agent to pick encryption method across either supported Python version.

If you choose to modify the base agent, be sure to duplicate your changes across both `.py2` and `.py3` files to maintain compatibility (if your changes are indeed supported across both versions).

## Adding C2 Profiles

Medusa currently only supported the HTTP C2 profile and will need some refactoring to easily support others. Watch this space though!