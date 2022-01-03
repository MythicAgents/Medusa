from mythic_payloadtype_container.MythicCommandBase import *
import json
from mythic_payloadtype_container.MythicRPC import *

class PipFreezeArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class PipFreezeCommand(CommandBase):
    cmd = "pip_freeze"
    needs_admin = False
    help_cmd = "pip_freeze"
    description = "This programmatically lists all installed modules."
    version = 1
    is_exit = False
    is_file_browse = False
    is_process_list = False
    is_download_file = False
    is_remove_file = False
    is_upload_file = False
    author = "@ajpc500"
    argument_class = PipFreezeArguments
    attackmapping = []
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[ SupportedOS.MacOS, SupportedOS.Windows, SupportedOS.Linux ],
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        return task

    async def process_response(self, response: AgentResponse):
        pass
