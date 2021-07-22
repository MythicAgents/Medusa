from mythic_payloadtype_container.MythicCommandBase import *
import json
from mythic_payloadtype_container.MythicRPC import *
import sys


class EvalArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "command": CommandParameter(
                name="command",
                type=ParameterType.String,
                description="Command to evaluate in Python interpreter",
            )
        }

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            self.add_arg("command", self.command_line)


class EvalCommand(CommandBase):
    cmd = "eval_code"
    needs_admin = False
    help_cmd = "eval_code python-code"
    description = "Evaluate python code in interpreter"
    version = 1
    author = "@ajpc500"
    attackmapping = []
    argument_class = EvalArguments
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[SupportedOS.MacOS, SupportedOS.Windows, SupportedOS.Linux ],
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        task.display_params = task.args.get_arg("command")
        return task

    async def process_response(self, response: AgentResponse):
        pass
