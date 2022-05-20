from mythic_payloadtype_container.MythicCommandBase import *


class WhoamiArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {}

    async def parse_arguments(self):
        pass


class WhoamiCommand(CommandBase):
    cmd = "whoami"
    needs_admin = False
    help_cmd = "whoami"
    description = "Prints the effective username for the agent"
    version = 1
    author = "@mihaid-b"
    attackmapping = ["T1033"]
    argument_class = WhoamiArguments

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        return task

    async def process_response(self, response: AgentResponse):
        pass
