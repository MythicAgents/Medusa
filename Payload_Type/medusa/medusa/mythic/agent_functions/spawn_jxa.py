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
    
    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )

        try:
            file_resp = await SendMythicRPCFileSearch(MythicRPCFileSearchMessage(
                TaskID=taskData.Task.ID,
                AgentFileID=taskData.args.get_arg("file"),
            ))

            if file_resp.Success:
                if len(file_resp.Files) > 0:
                    response.DisplayParams = f"Spawning osascript and loading script: {file_resp.Files[0].Filename}"
                elif len(file_resp.response) == 0:
                    raise Exception("Failed to find the named file. Have you uploaded it before? Did it get deleted?")
            else:
                raise Exception("Error from Mythic RPC: " + str(file_resp.error))
        
            file_resp = await SendMythicRPCFileUpdate(MythicRPCFileUpdateMessage(
                AgentFileID=taskData.args.get_arg("file"),
                DeleteAfterFetch=True,
                Comment="Uploaded for spawn_jxa"
            ))
        
        except Exception as e:
            raise Exception("Error from Mythic: " + str(sys.exc_info()[-1].tb_lineno) + str(e))
        
        return response
        

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
