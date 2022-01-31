from mythic_payloadtype_container.MythicCommandBase import *
import json, re
from mythic_payloadtype_container.MythicRPC import *
import sys


class KillArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="process_id",
                type=ParameterType.Number,
                description="ID of Process to Terminate",
            )
        ]

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            self.add_arg("process_id", self.command_line)
        
    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class KillCommand(CommandBase):
    cmd = "kill"
    needs_admin = False
    help_cmd = "kill process_id"
    description = "Terminate process by ID"
    version = 1
    author = "@ajpc500"
    attackmapping = []
    supported_ui_features = [ "process_browser:kill" ] 
    argument_class = KillArguments
    attributes = CommandAttributes(
        supported_python_versions=["Python 3.8"],
        supported_os=[ SupportedOS.Windows ],
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        task.display_params = f"Terminating process with PID: " + str(task.args.get_arg("process_id"))
        return task

    async def process_response(self, response: AgentResponse):
        pass
