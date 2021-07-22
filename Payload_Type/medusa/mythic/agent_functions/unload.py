from mythic_payloadtype_container.MythicCommandBase import *
from mythic_payloadtype_container.MythicRPC import *
import json, base64, os

class UnloadArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "command": CommandParameter(
                name="command", 
                type=ParameterType.ChooseOne, 
                default_value=[], 
                dynamic_query_function=self.get_commands
            )
        }

    async def get_commands(self, callback: dict) -> [str]:
        resp = await MythicRPC().execute("get_callback_commands", callback_id=callback["id"], loaded_only=True)
        return [ cmd["cmd"] for cmd in resp.response ]

        # cmds = [ ]
        # py_suffix = ".py2" if callback["build_parameters"]["python_version"] == "Python 2.7" else ".py3"
        # for func in os.listdir(self.agent_code_path):
            # if (func.endswith(py_suffix) or func.endswith(".py")) and "base_agent" not in func:
            # cmds.append(func)
        # return cmds 
    
    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == "{":
                self.load_args_from_json_string(self.command_line)
            else:
                self.add_arg("command", self.command_line)
        else:
            raise ValueError("Missing arguments")
        # self.add_arg("py_ver", callback["build_parameters"]["python_version"])


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