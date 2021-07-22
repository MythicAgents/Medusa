from mythic_payloadtype_container.MythicCommandBase import *
import json
from mythic_payloadtype_container.MythicRPC import *
import sys


class RmArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "path": CommandParameter(
                name="path",
                type=ParameterType.String,
                required=True,
                description="Read and output the content of a file",
            )
        }

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            self.add_arg("path", self.command_line)


class RmCommand(CommandBase):
    cmd = "rm"
    needs_admin = False
    help_cmd = "rm /path/to/file"
    description = "Delete a file or folder"
    version = 1
    author = "@ajpc500"
    attackmapping = [ "T1485" ]
    supported_ui_features = ["file_browser:remove"]
    argument_class = RmArguments
    browser_script = [BrowserScript(script_name="ls", author="@its_a_feature_")]
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[SupportedOS.MacOS, SupportedOS.Windows, SupportedOS.Linux ],
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        task.display_params = "Deleting " + str(task.args.get_arg("path"))
        return task

    async def process_response(self, response: AgentResponse):
        pass
