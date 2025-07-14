from mythic_container.MythicCommandBase import *
import json, re
from mythic_container.MythicRPC import *
import sys


class EvalArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="command",
                type=ParameterType.String,
                description="Command to execute in Python interpreter",
            )
        ]

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            self.add_arg("command", self.command_line)
        
    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class ExecCommand(CommandBase):
    cmd = "exec_code"
    needs_admin = False
    help_cmd = "exec_code python-code"
    description = "Execute python code in interpreter"
    version = 1
    author = "@RioT"
    attackmapping = []
    argument_class = EvalArguments
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[SupportedOS.MacOS, SupportedOS.Windows, SupportedOS.Linux ],
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        task.display_params = task.args.get_arg("command")
        return task

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
