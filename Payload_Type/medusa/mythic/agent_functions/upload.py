from mythic_payloadtype_container.MythicCommandBase import *
from mythic_payloadtype_container.MythicRPC import *
import json
import sys
import base64

class UploadArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="file", 
                type=ParameterType.File, 
                description="file to upload"
            ),
            CommandParameter(
                name="remote_path",
                type=ParameterType.String,
                description="/remote/path/on/victim.txt",
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply arguments")
        raise ValueError("Must supply named arguments or use the modal")

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class UploadCommand(CommandBase):
    cmd = "upload"
    needs_admin = False
    help_cmd = "upload"
    description = (
        "Upload a file to the target machine by selecting a file from your computer. "
    )
    version = 1
    supported_ui_features = ["file_browser:upload"]
    author = "@its_a_feature_"
    attackmapping = ["T1132", "T1030", "T1105"]
    argument_class = UploadArguments
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[SupportedOS.MacOS, SupportedOS.Windows, SupportedOS.Linux ],
    )


    async def create_tasking(self, task: MythicTask) -> MythicTask:
        try:
            file_resp = await MythicRPC().execute(
                "get_file", 
                task_id=task.id,
                file_id=task.args.get_arg("file"),
                get_contents=False)
            if file_resp.status == MythicRPCStatus.Success:
                original_file_name = file_resp.response[0]["filename"]
                if len(task.args.get_arg("remote_path")) == 0:
                    task.args.add_arg("remote_path", original_file_name)
                elif task.args.get_arg("remote_path")[-1] == "/":
                    task.args.add_arg("remote_path", task.args.get_arg("remote_path") + original_file_name)
                    # task.args.add_arg("file", file_resp.response["agent_file_id"])
                task.display_params = f"{original_file_name} to {task.args.get_arg('remote_path')}"
            else:
                raise Exception("Error from Mythic RPC: " + str(file_resp.error))
        
            file_resp = await MythicRPC().execute("update_file",
                file_id=task.args.get_arg("file"),
                delete_after_fetch=True,
                comment="Uploaded to disk for upload")

        
        except Exception as e:
            raise Exception("Error from Mythic: " + str(sys.exc_info()[-1].tb_lineno) + str(e))
        return task

    async def process_response(self, response: AgentResponse):
        pass
