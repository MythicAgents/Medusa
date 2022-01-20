from mythic_payloadtype_container.MythicCommandBase import *
from mythic_payloadtype_container.MythicRPC import *
import json
import sys
import base64

class ShinjectArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="shellcode", 
                type=ParameterType.File, 
                description="Shellcode to inject"
            ),
            CommandParameter(
                name="pid",
                type=ParameterType.Number,
                description="ID of process to inject into",
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == "{":
                self.load_args_from_json_string(self.command_line)
            else:
                raise ValueError("Missing JSON arguments")
        else:
            raise ValueError("Missing arguments")


class ShinjectCommand(CommandBase):
    cmd = "shinject"
    needs_admin = False
    help_cmd = "shinject"
    description = (
        "Inject shellcode from local file into target process"
    )
    version = 1
    supported_ui_features = ["process:inject"]
    author = "@ajpc500"
    attackmapping = [ "T1055" ]

    argument_class = ShinjectArguments
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[ SupportedOS.Windows ]
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        original_file_name = json.loads(task.original_params)['shellcode']
        file_resp = await MythicRPC().execute(
                "get_file", 
                task_id=task.id,
                file_id=task.args.get_arg("file"),
                get_contents=False
            )
        if file_resp.status == MythicStatus.Success:
            task.args.add_arg("shellcode", file_resp.response['agent_file_id'])
        task.display_params = "Injecting {} into PID {}".format(original_file_name, task.args.get_arg("pid"))
        return task

    async def process_response(self, response: AgentResponse):
        pass
