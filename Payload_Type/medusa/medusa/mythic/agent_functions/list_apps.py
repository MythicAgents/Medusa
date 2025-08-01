from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *

class ListAppsArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class ListAppsCommand(CommandBase):
    cmd = "list_apps"
    needs_admin = False
    help_cmd = "list_apps"
    description = "This lists all running applications"
    version = 1
    is_exit = False
    is_file_browse = False
    is_process_list = False
    is_download_file = False
    is_remove_file = False
    is_upload_file = False
    author = "@ajpc500"
    argument_class = ListAppsArguments
    attackmapping = []
    browser_script = BrowserScript(script_name="list_apps", author="@ajpc500", for_new_ui=True)
    attributes = CommandAttributes(
        filter_by_build_parameter={
            "python_version": "Python 2.7"
        },
        supported_python_versions=["Python 2.7"],
        supported_os=[SupportedOS.MacOS],
    )
    
    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )

        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
                    TaskID=taskData.Task.ID,
                    ArtifactMessage=f"NSWorkspace.sharedWorkspace().runningApplications()",
                    BaseArtifactType="API Called"
                ))

        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
