from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json

def positiveTime(val):
    if val < 0:
        raise ValueError("Value must be positive")

class SleepArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="jitter",
                type=ParameterType.Number,
                validation_func=positiveTime,
                default_value=-1,
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                    ui_position=2
                )],
                description="Percentage of C2's interval to use as jitter",
            ),
            CommandParameter(
                name="seconds",
                type=ParameterType.Number,
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    ui_position=1
                )],
                validation_func=positiveTime,
                description="Number of seconds between checkins",
            ),
        ]

    async def parse_arguments(self):
        if self.command_line[0] != "{":
            pieces = self.command_line.split(" ")
            if len(pieces) == 1:
                self.add_arg("seconds", pieces[0])
                self.remove_arg("jitter")
            elif len(pieces) == 2:
                self.add_arg("seconds", pieces[0])
                self.add_arg("jitter", pieces[1])
            else:
                raise Exception("Wrong number of parameters, should be 1 or 2")
        else:
            self.load_args_from_json_string(self.command_line)

class SleepCommand(CommandBase):
    cmd = "sleep"
    needs_admin = False
    help_cmd = "sleep seconds jitter_percentage"
    description = "set sleep and jitter"
    version = 1
    author = "@ajpc500"
    attackmapping = []
    argument_class = SleepArguments
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[SupportedOS.MacOS, SupportedOS.Windows, SupportedOS.Linux ],
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        task.display_params = str(task.args.get_arg("seconds")) + "s"
        if int(task.args.get_arg("jitter")) != -1:
            task.display_params += " with " + str(task.args.get_arg("jitter")) + "% jitter"
        return task
    
    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        
        seconds = taskData.args.get_arg("seconds")
        jitter = taskData.args.get_arg("jitter")

        if jitter == -1:
            response.DisplayParams = f"Setting sleep to {seconds} seconds"
        else:
            response.DisplayParams = f"Setting sleep to {seconds} seconds with {jitter}% jitter"

        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        await SendMythicRPCCallbackUpdate(MythicRPCCallbackUpdateMessage(
            TaskID=task.Task.ID,
            SleepInfo=response,
        ))
        return resp