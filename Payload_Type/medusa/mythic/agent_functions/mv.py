from mythic_payloadtype_container.MythicCommandBase import *
from mythic_payloadtype_container.MythicRPC import *
import json

class MvArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="destination",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    ui_position=2
                )],
                description="Location for moved file or folder",
            ),
            CommandParameter(
                name="source",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    ui_position=1
                )],
                description="Path to file or folder for moving",
            ),
        ]

    async def parse_arguments(self):
        if self.command_line[0] != "{":
            pieces = self.command_line.split(" ")
            if len(pieces) == 2:
                self.add_arg("source", pieces[0])
                self.add_arg("destination", pieces[1])
            else:
                raise Exception("Wrong number of parameters, should be 2")
        else:
            self.load_args_from_json_string(self.command_line)

class MvCommand(CommandBase):
    cmd = "mv"
    needs_admin = False
    help_cmd = "mv source destination"
    description = "Move file or folder to destination"
    version = 1
    author = "@ajpc500"
    attackmapping = []
    argument_class = MvArguments
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[SupportedOS.MacOS, SupportedOS.Windows, SupportedOS.Linux ],
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        task.display_params = "Moving " + str(task.args.get_arg("source")) + " to "
        task.display_params += str(task.args.get_arg("destination"))
        return task

    async def process_response(self, response: AgentResponse):
        pass
