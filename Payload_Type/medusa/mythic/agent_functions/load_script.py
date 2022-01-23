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
        file_resp = await MythicRPC().execute(
                "get_file", 
                task_id=task.id,
                file_id=task.args.get_arg("file"),
                get_contents=False
            )
        if file_resp.status == MythicStatus.Success:
            original_file_name = file_resp.response[0]["filename"]
            task.display_params = f"Loading script: {original_file_name}"
        else:
            raise Exception("Failed to register file: " + file_resp.error)
        
        file_resp = await MythicRPC().execute("update_file",
                file_id=task.args.get_arg("file"),
                delete_after_fetch=True,
                comment="Uploaded into memory for load_script")
        
        
        return task

    async def process_response(self, response: AgentResponse):
        pass
