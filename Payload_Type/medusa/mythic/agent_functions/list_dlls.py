from mythic_payloadtype_container.MythicCommandBase import *
from mythic_payloadtype_container.MythicRPC import *
import json

class ListDllsArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="process_id",
                type=ParameterType.Number,
                default_value=0,
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                )],
                description="ID of process to list loaded DLLs of, can be 0 for local process",
            )
        ]

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == '{':
                temp_json = json.loads(self.command_line)
                self.add_arg("process_id", temp_json["process_id"])
            else:
                self.add_arg("process_id", self.command_line)
        
    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)

class ListDllsCommand(CommandBase):
    cmd = "list_dlls"
    needs_admin = False
    help_cmd = "list_dlls [process_id]"
    description = "List DLLs loaded in current or specified process"
    version = 1
    is_exit = False
    is_file_browse = False
    is_process_list = False
    is_download_file = False
    is_remove_file = False
    is_upload_file = False
    author = "@ajpc500"
    supported_ui_features = ["process_dlls:list"]

    argument_class = ListDllsArguments
    attackmapping = []
    browser_script = [
        BrowserScript(script_name="list_dlls", author="@its_a_feature_", for_new_ui=True)
    ]
    attributes = CommandAttributes(
        supported_python_versions=["Python 3.8"],
        supported_os=[ SupportedOS.Windows ],
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        process_id = task.args.get_arg("process_id")
        if process_id == 0:
            task.display_params = f"Listing DLLs loaded in current process"
        else:
            task.display_params = f"Listing DLLs loaded in process with PID: {process_id}"
        return task

    async def process_response(self, response: AgentResponse):
        pass
