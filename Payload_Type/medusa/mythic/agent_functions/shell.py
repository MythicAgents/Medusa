from mythic_payloadtype_container.MythicCommandBase import *
from mythic_payloadtype_container.MythicRPC import *


class ShellArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "command": CommandParameter(
                name="command", type=ParameterType.String, description="Command to run"
            ),
        }

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == "{":
                self.load_args_from_json_string(self.command_line)
            else:
                self.add_arg("command", self.command_line)
        else:
            raise ValueError("Missing arguments")

class ShellCommand(CommandBase):
    cmd = "shell"
    needs_admin = False
    help_cmd = "shell {command}"
    description = "This runs {command} in a terminal."
    version = 1
    author = "@ajpc500"
    attackmapping = ["T1059"]
    argument_class = ShellArguments
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[ SupportedOS.MacOS, SupportedOS.Linux, SupportedOS.Windows ]
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        task.display_params = task.args.get_arg("command")
        return task

    async def process_response(self, response: AgentResponse):
        pass
