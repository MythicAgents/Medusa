from mythic_payloadtype_container.MythicCommandBase import *
from mythic_payloadtype_container.MythicRPC import *
import json
import sys
import base64

class LoadScriptArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="file", 
                type=ParameterType.File, 
                description="script to load"
            )
        ]

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == "{":
                self.load_args_from_json_string(self.command_line)
            else:
                raise ValueError("Missing JSON arguments")
        else:
            raise ValueError("Missing arguments")


class LoadScriptCommand(CommandBase):
    cmd = "load_script"
    needs_admin = False
    help_cmd = "load_script"
    description = (
        "Load a Python script into the agent. Functions in the script can be added to the agent class with setattr() and called with the eval_code function if needed"
    )
    version = 1
    author = "@ajpc500"
    attackmapping = []
    argument_class = LoadScriptArguments
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[SupportedOS.MacOS, SupportedOS.Windows, SupportedOS.Linux ],
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        file_resp = await MythicRPC().execute("create_file", task_id=task.id,
            file=base64.b64encode(task.args.get_arg("file")).decode(),
            delete_after_fetch=True,
        )
        if file_resp.status == MythicStatus.Success:
            task.args.add_arg("file", file_resp.response["agent_file_id"])
        else:
            raise Exception("Failed to register file: " + file_resp.error)
        return task

    async def process_response(self, response: AgentResponse):
        pass
