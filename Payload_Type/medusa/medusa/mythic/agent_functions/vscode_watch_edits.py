from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json


class VscodeWatchEditsArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="backups_path",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=False
                )],
                description="Path of VSCode backups folder ",
            ),
            CommandParameter(
                name="seconds",
                type=ParameterType.Number,
                parameter_group_info=[ParameterGroupInfo(
                    required=False
                )],
                default_value=60, 
                description="Seconds to wait between polling directory for changes",
            )
        ]

    async def parse_arguments(self):
        if self.command_line[0] != "{":
            pieces = self.command_line.split(" ")
            if len(pieces) == 2:
                self.add_arg("backups_path", pieces[0])
                self.add_arg("seconds", pieces[1])
            else:
                raise Exception("Wrong number of parameters, should be 2")
        else:
            self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class VscodeWatchEditsCommand(CommandBase):
    cmd = "vscode_watch_edits"
    needs_admin = False
    help_cmd = "vscode_watch_edits [/path/to/backups/dir]"
    description = "Poll VSCode backups directory for unsaved edits"
    version = 1
    author = "@ajpc500"
    attackmapping = ["T1083"]
    argument_class = VscodeWatchEditsArguments
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[SupportedOS.MacOS],
    )
    
    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        
        if taskData.args.get_arg("backups_path"):
            response.DisplayParams = f"Watching for VSCode edits. Polling '{taskData.args.get_arg('backups_path')}' for changes every {taskData.args.get_arg('seconds')} seconds"
        else:
            response.DisplayParams = "Watching for VSCode edits. Polling '~/Library/Application Support/Code/Backups' for changes every {} seconds".format(taskData.args.get_arg("seconds"))

        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
