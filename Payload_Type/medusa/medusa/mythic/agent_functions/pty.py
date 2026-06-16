from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


class PtyArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="mode",
                cli_name="mode",
                display_name="Mode",
                type=ParameterType.ChooseOne,
                choices=["spawn", "self", "fork"],
                default_value="spawn",
                description="spawn: PTY + child process. self: in-process Python REPL with live agent state. fork: forked Python REPL with snapshotted agent state and full PTY.",
                parameter_group_info=[ParameterGroupInfo(
                    required=False
                )],
            ),
            CommandParameter(
                name="program_path",
                cli_name="program_path",
                display_name="Program Path",
                type=ParameterType.String,
                description="What program to spawn with a PTY (spawn mode only)",
                default_value="/bin/bash",
                parameter_group_info=[ParameterGroupInfo(
                    required=False
                )],
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            self.add_arg("mode", "spawn")
            self.add_arg("program_path", "/bin/bash")
        else:
            try:
                self.load_args_from_json_string(self.command_line)
            except:
                parts = self.command_line.strip().split()
                mode = "spawn"
                program = "/bin/bash"
                for p in parts:
                    if p in ("self", "fork", "spawn"):
                        mode = p
                    else:
                        program = p
                self.add_arg("mode", mode)
                self.add_arg("program_path", program)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class PtyCommand(CommandBase):
    cmd = "pty"
    needs_admin = False
    help_cmd = "pty [/bin/bash]\npty self\npty fork"
    description = "Open an interactive PTY session. Modes: 'spawn' (default) runs a program with a PTY, 'self' opens an in-process Python REPL with live agent state, 'fork' forks the agent and opens a Python REPL with snapshotted state and full PTY support."
    version = 2
    author = "@ajpc500"
    attackmapping = ["T1059"]
    argument_class = PtyArguments
    supported_ui_features = ["task_response:interactive"]
    attributes = CommandAttributes(
        supported_python_versions=["Python 3.8", "Python 2.7"],
        supported_os=[SupportedOS.MacOS, SupportedOS.Linux],
    )

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        mode = taskData.args.get_arg("mode")
        program_path = taskData.args.get_arg("program_path")
        if mode == "spawn":
            response.DisplayParams = "{} ({})".format(program_path, mode)
        else:
            response.DisplayParams = mode
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
