from mythic_payloadtype_container.MythicCommandBase import *
import json
from mythic_payloadtype_container.MythicRPC import *
import sys


class RmArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="path",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=True
                )],
                description="Read and output the content of a file",
            )
        ]

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == "{":
                temp_json = json.loads(self.command_line)
                if "host" in temp_json:
                    # this means we have tasking from the file browser rather than the popup UI
                    # the apfell agent doesn't currently have the ability to do _remote_ listings, so we ignore it
                    self.add_arg("path", temp_json["path"] + "/" + temp_json["file"])
                else:
                    self.add_arg("path", temp_json["path"])
            else:
                self.add_arg("path", self.command_line)
        else:
            raise ValueError("Missing arguments")


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
