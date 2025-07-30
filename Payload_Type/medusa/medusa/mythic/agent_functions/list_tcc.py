from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *
import sys


class ListTccArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="db",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=True
                )],
                default_value="/Library/Application Support/com.apple.TCC/TCC.db",
                description="Path to TCC database",
            )
        ]

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == '{':
                temp_json = json.loads(self.command_line)
                self.add_arg("db", temp_json["db"])
            else:
                self.add_arg("db", self.command_line)
        else:
            self.add_arg("db", "/Library/Application Support/com.apple.TCC/TCC.db")
        self.add_arg("tcc", True, type=ParameterType.Boolean)

class ListTccCommand(CommandBase):
    cmd = "list_tcc"
    needs_admin = False
    help_cmd = "list_tcc [db_path]"
    description = "Lists entries in TCC database (requires Full Disk Access)"
    version = 1
    author = "@ajpc500"
    attackmapping = []
    supported_ui_features = []
    argument_class = ListTccArguments
    browser_script = BrowserScript(script_name="tcc", author="@ajpc500", for_new_ui=True)
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
        
        response.DisplayParams = "Listing TCC database entries from " + taskData.Task.Args.get_arg("db")
        
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
