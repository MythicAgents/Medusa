from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json

class ListModulesArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="module_name",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=False
                )],
                description="Provide full file listing for a loaded module.",
            )
        ]

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == "{":
                self.load_args_from_json_string(self.command_line)
            else:
                self.add_arg("module_name", self.command_line)

class ListModulesCommand(CommandBase):
    cmd = "list_modules"
    needs_admin = False
    help_cmd = "list_modules [module_name]"
    description = "List Python modules loaded in-memory, or a full file listing for a specific module"
    version = 1
    is_exit = False
    is_file_browse = False
    is_process_list = False
    is_download_file = False
    is_remove_file = False
    is_upload_file = False
    author = "@ajpc500"
    argument_class = ListModulesArguments
    attackmapping = []
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[ SupportedOS.MacOS, SupportedOS.Windows, SupportedOS.Linux ],
    )

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        
        if taskData.args.get_arg("module_name"):
            response.DisplayParams = f"Listing files for module: {taskData.Task.Args.get_arg('module_name')}"
        else:
            response.DisplayParams = "Listing modules loaded in-memory"

        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
