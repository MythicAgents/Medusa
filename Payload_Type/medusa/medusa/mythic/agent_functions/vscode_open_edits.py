from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *
import sys


class VscodeOpenEditsArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="backups_path",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=False
                )],
                default_value="",
                description="Path to VSCode backups directory",
            )
        ]

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            self.add_arg("backups_path", self.command_line)
        
    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)

class VscodeOpenEditsCommand(CommandBase):
    cmd = "vscode_open_edits"
    needs_admin = False
    help_cmd = "vscode_open_edits [backups_dir_path]"
    description = "Lists edited files in VSCode that have not been saved."
    version = 1
    author = "@ajpc500"
    attackmapping = []
    supported_ui_features = []
    argument_class = VscodeOpenEditsArguments
    browser_script = BrowserScript(script_name="vscode_edits", author="@ajpc500", for_new_ui=True)
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[
            SupportedOS.MacOS
        ],
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        if task.args.get_arg("backups_path"):
            task.display_params = "Listing edited and unsaved files in VSCode from backup directory: " + task.args.get_arg("backups_path")
        else:
            task.display_params = "Listing edited and unsaved files in VSCode from backup directory: '~/Library/Application Support/Code/Backups'"
        return task

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
