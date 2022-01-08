from mythic_payloadtype_container.MythicCommandBase import *
from mythic_payloadtype_container.MythicRPC import *
import json, base64, os

class UnloadArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="command", 
                type=ParameterType.ChooseOne, 
                description="Command to unload from the agent",
                default_value=[], 
                choices_are_all_commands=True,
                choices_are_loaded_commands=True
            )
        ]
            
    async def parse_arguments(self):
        if self.command_line[0] != "{":
            self.add_arg("command", self.command_line)
        else:
            self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class UnloadCommand(CommandBase):
    cmd = "unload"
    needs_admin = False
    help_cmd = "unload cmd"
    description = "This unloads an existing function from a callback."
    version = 1
    author = "@ajpc500"
    parameters = []
    attackmapping = ["T1030", "T1129"]
    argument_class = UnloadArguments
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[SupportedOS.MacOS, SupportedOS.Windows, SupportedOS.Linux ],
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        return task


    async def process_response(self, response: AgentResponse):
        pass