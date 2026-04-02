from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class DownloadBulkArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="path",
                type=ParameterType.Array,
                default_value=[],
                description="Paths of file(s) or director(ies) to download.",
                parameter_group_info=[ParameterGroupInfo(
                    required=True
                )]
            ),
            CommandParameter(
                name="mode",
                type=ParameterType.ChooseOne,
                choices=["archive", "iterative"],
                default_value="archive",
                description=(
                    "Download mode: 'archive' bundles all files into a single in-memory zip archive, "
                    "'iterative' sends each file individually."
                ),
                parameter_group_info=[ParameterGroupInfo(
                    required=False
                )]
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise Exception(
                "Require a path to download.\n\tUsage: {}".format(DownloadBulkCommand.help_cmd)
            )

        if self.command_line[0] == "{":
            temp_json = json.loads(self.command_line)
            if "path" in temp_json:
                path_val = temp_json["path"]
                if isinstance(path_val, str):
                    temp_json["path"] = [path_val]
            self.load_args_from_dictionary(temp_json)
        else:
            raw = self.command_line
            if (raw[0] == '"' and raw[-1] == '"') or (raw[0] == "'" and raw[-1] == "'"):
                raw = raw[1:-1]
            self.add_arg("path", [raw])


class DownloadBulkCommand(CommandBase):
    cmd = "download_bulk"
    needs_admin = False
    help_cmd = 'download_bulk {"path": ["/remote/path", "/remote/path2"], "mode": "archive"}'
    description = (
        "Bulk download file(s), director(ies), or a mix from the target machine. "
        "Use 'archive' mode to bundle everything into a single in-memory zip, "
        "or 'iterative' mode to transfer each file individually."
    )
    version = 1
    is_download_file = True
    author = "@maclarel"
    parameters = []
    attackmapping = ["T1020", "T1030", "T1041"]
    argument_class = DownloadBulkArguments
    browser_script = BrowserScript(script_name="download_bulk", author="@maclarel", for_new_ui=True)
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[SupportedOS.MacOS, SupportedOS.Windows, SupportedOS.Linux],
    )

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        paths = taskData.args.get_arg("path")
        mode = taskData.args.get_arg("mode") or "archive"
        display = ", ".join(paths) if isinstance(paths, list) else str(paths)
        response.DisplayParams = f"{display} (mode: {mode})"
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
