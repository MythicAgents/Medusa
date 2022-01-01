from mythic_payloadtype_container.MythicCommandBase import *
from mythic_payloadtype_container.MythicRPC import *
import json
import sys
import base64

class LoadModuleArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="file", type=ParameterType.File, description="Zipped library to upload"
            ),
            CommandParameter(
                name="module_name",
                type=ParameterType.String,
                description="Name of module to load, e.g. cryptography"
            )
        ]

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == "{":
                self.load_args_from_json_string(self.command_line)
            else:
                raise ValueError("Missing JSON arguments")
        else:
            raise ValueError("Missing arguments")


class LoadModuleCommand(CommandBase):
    cmd = "load_module"
    needs_admin = False
    help_cmd = "load_module"
    description = (
        "Upload a python library and load it in-memory"
    )
    version = 1
    author = "@ajpc500"
    attackmapping = []
    argument_class = LoadModuleArguments
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[SupportedOS.MacOS, SupportedOS.Windows, SupportedOS.Linux ],
    )


    async def create_tasking(self, task: MythicTask) -> MythicTask:
        try:
            file_resp = await MythicRPC().execute("create_file", task_id=task.id,
                file=base64.b64encode(task.args.get_arg("file")).decode(),
                delete_after_fetch=True,
            )
            if file_resp.status == MythicStatus.Success:
                task.args.add_arg("file", file_resp.response["agent_file_id"])
                task.display_params = f"Loading {task.args.get_arg('module_name')} module into memory"
            else:
                raise Exception("Error from Mythic: " + str(file_resp.error))
        except Exception as e:
            raise Exception("Error from Mythic: " + str(sys.exc_info()[-1].tb_lineno) + str(e))
        return task

    async def process_response(self, response: AgentResponse):
        pass
