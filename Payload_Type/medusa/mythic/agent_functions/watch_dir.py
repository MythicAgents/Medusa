from mythic_payloadtype_container.MythicCommandBase import *
from mythic_payloadtype_container.MythicRPC import *
import json


class WatchDirArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "path": CommandParameter(
                name="path",
                type=ParameterType.String,
                required=False,
                description="Path of folder on the current system to watch",
            ),
            "seconds": CommandParameter(
                name="seconds",
                type=ParameterType.Number,
                required=False,
                default_value=60, 
                description="Seconds to wait between polling directory for changes",
            )
        }

    async def parse_arguments(self):
        if self.command_line[0] != "{":
            pieces = self.command_line.split(" ")
            if len(pieces) == 2:
                self.add_arg("path", pieces[0])
                self.add_arg("seconds", pieces[1])
            else:
                raise Exception("Wrong number of parameters, should be 2")
        else:
            self.load_args_from_json_string(self.command_line)

class WatchDirCommand(CommandBase):
    cmd = "watch_dir"
    needs_admin = False
    help_cmd = "watch_dir [/path/to/file]"
    description = "Poll a directory for changes"
    version = 1
    author = "@ajpc500"
    attackmapping = ["T1083"]
    argument_class = WatchDirArguments
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[SupportedOS.MacOS, SupportedOS.Windows, SupportedOS.Linux ],
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        task.display_params = "Polling {} for changes every {} seconds".format(task.args.get_arg("path"), str(task.args.get_arg("seconds")))
        return task

    async def process_response(self, response: AgentResponse):
        pass
