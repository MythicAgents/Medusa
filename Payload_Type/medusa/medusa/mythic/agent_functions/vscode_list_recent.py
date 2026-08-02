from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *
import sys


class VscodeListRecentArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="db",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=False
                )],
                default_value="",
                description="Path to VSCode state database",
            )
        ]

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            self.add_arg("db", self.command_line)
        
    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)

class VscodeListRecentCommand(CommandBase):
    cmd = "vscode_list_recent"
    needs_admin = False
    help_cmd = "vscode_list_recent [state_db_path]"
    description = "Lists recently accessed files/folders in VSCode state database"
    version = 1
    author = "@ajpc500"
    attackmapping = []
    supported_ui_features = []
    argument_class = VscodeListRecentArguments
    browser_script = BrowserScript(script_name="vscode_recent", author="@ajpc500", for_new_ui=True)
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[
            SupportedOS.MacOS
        ],
    )

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        
        if taskData.args.get_arg("db"):
            response.DisplayParams = f"Listing recent VSCode files from state database at {taskData.args.get_arg('db')}"
        else:
            response.DisplayParams = "Listing recent VSCode files from default state database at '~/Library/Application Support/Code/User/globalStorage/state.vscdb'"

        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
