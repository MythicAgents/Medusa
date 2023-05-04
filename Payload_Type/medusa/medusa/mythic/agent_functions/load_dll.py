from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json

class LoadDllArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="dllpath",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    ui_position=1
                )],
                description="Location of on-disk DLL",
            ),
            CommandParameter(
                name="dllexport",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    ui_position=2
                )],
                description="Export of target DLL",
            ),
        ]

    async def parse_arguments(self):
        if self.command_line[0] != "{":
            pieces = self.command_line.split(" ")
            if len(pieces) == 2:
                self.add_arg("dllpath", pieces[0])
                self.add_arg("dllexport", pieces[1])
            else:
                raise Exception("Wrong number of parameters, should be 2")
        else:
            self.load_args_from_json_string(self.command_line)

class LoadDllCommand(CommandBase):
    cmd = "load_dll"
    needs_admin = False
    help_cmd = "load_dll dll_path dll_export"
    description = "Load DLL from disk"
    version = 1
    author = "@ajpc500"
    attackmapping = [ "T1059.006", "T1127" ]
    argument_class = LoadDllArguments
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[SupportedOS.Windows],
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        task.display_params = "Executing " + str(task.args.get_arg("dllpath")) + " with export '"
        task.display_params += str(task.args.get_arg("dllexport")) + "'"
        return task

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
