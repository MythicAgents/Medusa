from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json


class WatchDirArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="path",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=True
                )],
                description="Path of folder on the current system to watch",
            ),
            CommandParameter(
                name="seconds",
                type=ParameterType.Number,
                parameter_group_info=[ParameterGroupInfo(
                    required=False
                )],
                default_value=60, 
                description="Seconds to wait between polling directory for changes",
            )
        ]

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

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


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

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
