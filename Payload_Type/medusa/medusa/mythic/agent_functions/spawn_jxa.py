from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json
import sys
import base64

class SpawnJxaArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="file", 
                type=ParameterType.File, 
                description="Script file to load"
            ),
            CommandParameter(
                name="language", 
                type=ParameterType.ChooseOne,
                choices=[ "JavaScript", "AppleScript" ],
                default_value="JavaScript", 
                description="Language of script to load"
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


class SpawnJxaCommand(CommandBase):
    cmd = "spawn_jxa"
    needs_admin = False
    help_cmd = "spawn_jxa"
    description = (
        "Spawn an osascript process and pipe script content to it."
    )
    version = 1
    author = "@ajpc500"
    attackmapping = []
    argument_class = SpawnJxaArguments
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[SupportedOS.MacOS ],
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        file_resp = await MythicRPC().execute(
                "get_file", 
                task_id=task.id,
                file_id=task.args.get_arg("file"),
                get_contents=False
            )
        if file_resp.status == MythicStatus.Success:
            original_file_name = file_resp.response[0]["filename"]
            task.display_params = f"Spawning osascript and loading script: {original_file_name}"
        else:
            raise Exception("Failed to register file: " + file_resp.error)
        
        file_resp = await MythicRPC().execute("update_file",
                file_id=task.args.get_arg("file"),
                delete_after_fetch=True,
                comment="Uploaded and piped to new osascript process")
        
        
        return task

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
