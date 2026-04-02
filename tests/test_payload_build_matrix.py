import asyncio
import importlib.util
import os
import pathlib
import py_compile
import re
import shutil
import sys
import tempfile
import types
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "Payload_Type" / "medusa" / "medusa" / "mythic" / "agent_functions" / "builder.py"
AGENT_CODE_PATH = ROOT / "Payload_Type" / "medusa" / "medusa" / "agent_code"
BASE_AGENT_PATH = AGENT_CODE_PATH / "base_agent"

PROFILES = ("http", "azure_blob")
PY_VERSIONS = ("Python 2.7", "Python 3.8")
CRYPTO_IMPLEMENTATIONS = {
    "manual_crypto": "No",
    "cryptography_lib": "Yes",
}


def discover_profiles():
    py2_profiles = {
        re.match(r"transport_(.+)\.py2$", p.name).group(1)
        for p in BASE_AGENT_PATH.glob("transport_*.py2")
        if re.match(r"transport_(.+)\.py2$", p.name)
    }
    py3_profiles = {
        re.match(r"transport_(.+)\.py3$", p.name).group(1)
        for p in BASE_AGENT_PATH.glob("transport_*.py3")
        if re.match(r"transport_(.+)\.py3$", p.name)
    }
    return tuple(sorted(py2_profiles.intersection(py3_profiles)))


PROFILES = discover_profiles()


def python_version_suffix(py_version):
    return "py2" if py_version == "Python 2.7" else "py3"


def parse_transport_sections(template_code: str):
    parts = re.split(r"###\s*(IMPORTS|CLASS_FIELDS|FUNCTIONS|CONFIG)\s*###", template_code)
    sections = {"IMPORTS": "", "CLASS_FIELDS": "", "FUNCTIONS": "", "CONFIG": ""}
    for i in range(1, len(parts), 2):
        sections[parts[i].strip()] = parts[i + 1].strip("\n")
    return sections


def function_names_from_code(code: str):
    return re.findall(r"^\s*def\s+([A-Za-z_]\w*)\s*\(", code, flags=re.MULTILINE)


def config_keys_from_code(code: str):
    return re.findall(r'"([A-Za-z0-9_]+)"\s*:', code)


def install_fake_mythic_modules():
    if "mythic_container" in sys.modules:
        return

    mythic_container = types.ModuleType("mythic_container")
    payload_builder = types.ModuleType("mythic_container.PayloadBuilder")
    command_base = types.ModuleType("mythic_container.MythicCommandBase")
    rpc_module = types.ModuleType("mythic_container.MythicRPC")

    class BuildStatus:
        Success = "success"
        Error = "error"

    class BuildResponse:
        def __init__(self, status=None):
            self.status = status
            self.build_stderr = ""
            self.build_message = ""
            self.payload = b""

        def set_status(self, status):
            self.status = status

    class BuildParameterType:
        ChooseOne = "ChooseOne"

    class BuildParameter:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class BuildStep:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class SupportedOS:
        Windows = "Windows"
        Linux = "Linux"
        MacOS = "MacOS"

    class PayloadType:
        def get_parameter(self, name):
            return self._params[name]

    class MythicRPCOtherServiceRPCMessage:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class MythicRPCPayloadUpdateBuildStepMessage:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    payload_builder.BuildStatus = BuildStatus
    payload_builder.BuildResponse = BuildResponse
    payload_builder.BuildParameterType = BuildParameterType
    payload_builder.BuildParameter = BuildParameter
    payload_builder.BuildStep = BuildStep
    payload_builder.PayloadType = PayloadType
    payload_builder.SupportedOS = SupportedOS

    rpc_module.MythicRPCOtherServiceRPCMessage = MythicRPCOtherServiceRPCMessage
    rpc_module.MythicRPCPayloadUpdateBuildStepMessage = MythicRPCPayloadUpdateBuildStepMessage

    sys.modules["mythic_container"] = mythic_container
    sys.modules["mythic_container.PayloadBuilder"] = payload_builder
    sys.modules["mythic_container.MythicCommandBase"] = command_base
    sys.modules["mythic_container.MythicRPC"] = rpc_module


def load_builder_module():
    install_fake_mythic_modules()
    spec = importlib.util.spec_from_file_location("medusa_builder_for_tests", BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeCommands:
    def get_commands(self):
        return ["cwd", "sleep"]


class FakeC2:
    def __init__(self, name, params):
        self._name = name
        self._params = params

    def get_c2profile(self):
        return {"name": self._name}

    def get_parameters_dict(self):
        return self._params


def base_c2_params():
    return {
        "callback_host": "http://127.0.0.1",
        "callback_port": "80",
        "post_uri": "/api/v1.4/agent_message",
        "get_uri": "/api/v1.4/agent_message",
        "query_path_name": "q",
        "proxy_host": "",
        "proxy_user": "",
        "proxy_pass": "",
        "proxy_port": "",
        "headers": "{}",
        "killdate": "2099-01-01",
        "callback_interval": "10",
        "callback_jitter": "5",
        "AESPSK": {
            "value": "aes256_hmac",
            "enc_key": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
            "dec_key": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
        },
        "encrypted_exchange_check": "true",
    }


async def fake_update_build_step(_msg):
    return None


async def fake_other_service_rpc(_msg):
    return types.SimpleNamespace(
        Success=True,
        Error="",
        Result={
            "blob_endpoint": "https://example.blob.core.windows.net",
            "container_name": "medusa",
            "sas_token": "sp=racwdl&sv=2025-07-05&sr=c&sig=abc",
        },
    )


class TestPayloadBuildMatrix(unittest.TestCase):
    def test_profiles_auto_discovered(self):
        self.assertTrue(PROFILES, "No transport profiles were discovered from transport_*.py2/.py3 templates")

    def _selected_values(self, env_name, allowed):
        selected = os.getenv(env_name, "").strip()
        if not selected:
            return allowed
        self.assertIn(selected, allowed, msg=f"Invalid {env_name}: {selected}")
        return (selected,)

    def _build_payload(self, profile_name, python_version, use_non_default_crypto):
        module = load_builder_module()
        module.SendMythicRPCPayloadUpdatebuildStep = fake_update_build_step
        module.SendMythicRPCOtherServiceRPC = fake_other_service_rpc

        medusa = module.Medusa()
        medusa.uuid = "11111111-1111-1111-1111-111111111111"
        medusa.commands = FakeCommands()
        medusa.agent_code_path = AGENT_CODE_PATH
        medusa._params = {
            "python_version": python_version,
            "use_non_default_cryptography_lib": use_non_default_crypto,
            "obfuscate_script": "No",
            "output": "py",
            "https_check": "Yes",
        }
        medusa.c2info = [FakeC2(profile_name, base_c2_params())]

        return asyncio.run(medusa.build())

    def _crypto_template_text(self, py_version, crypto_impl):
        suffix = python_version_suffix(py_version)
        crypto_file = "crypto_lib" if crypto_impl == "cryptography_lib" else "manual_crypto"
        return (BASE_AGENT_PATH / f"{crypto_file}.{suffix}").read_text().strip()

    def _transport_sections(self, py_version, profile):
        suffix = python_version_suffix(py_version)
        transport_code = (BASE_AGENT_PATH / f"transport_{profile}.{suffix}").read_text()
        return parse_transport_sections(transport_code)

    def test_dynamic_build_matrix(self):
        profiles = self._selected_values("TEST_PROFILE", PROFILES)
        py_versions = self._selected_values("TEST_PYTHON_VERSION", PY_VERSIONS)
        crypto_impls = self._selected_values("TEST_CRYPTO_IMPL", tuple(CRYPTO_IMPLEMENTATIONS.keys()))

        for profile in profiles:
            for py_version in py_versions:
                for crypto_impl in crypto_impls:
                    with self.subTest(profile=profile, py_version=py_version, crypto_impl=crypto_impl):
                        resp = self._build_payload(profile, py_version, CRYPTO_IMPLEMENTATIONS[crypto_impl])
                        self.assertEqual(resp.status, "success", msg=resp.build_stderr)
                        self.assertTrue(resp.payload)
                        source = resp.payload.decode()

                        self.assertNotIn("TRANSPORT_IMPORTS", source)
                        self.assertNotIn("TRANSPORT_CLASS_FIELDS", source)
                        self.assertNotIn("TRANSPORT_FUNCTIONS", source)
                        self.assertNotIn("TRANSPORT_CONFIG", source)
                        self.assertNotIn("### IMPORTS ###", source)
                        self.assertNotIn("### FUNCTIONS ###", source)

                        transport_sections = self._transport_sections(py_version, profile)
                        for func_name in function_names_from_code(transport_sections["FUNCTIONS"]):
                            self.assertIn(f"def {func_name}", source)

                        for config_key in config_keys_from_code(transport_sections["CONFIG"]):
                            self.assertIn(f'"{config_key}"', source)

                        params = base_c2_params()
                        if profile == "http":
                            self.assertIn(f'"Server": "{params["callback_host"]}"', source)
                        if profile == "azure_blob":
                            expected_result = asyncio.run(fake_other_service_rpc(None)).Result
                            self.assertIn(f'blob_endpoint = "{expected_result["blob_endpoint"]}"', source)
                            self.assertIn(f'container_name = "{expected_result["container_name"]}"', source)

                        crypto_template = self._crypto_template_text(py_version, crypto_impl)
                        self.assertIn(crypto_template, source)

                        if py_version == "Python 3.8":
                            compile(source, f"generated_{profile}_py3.py", "exec")

    def test_python3_payload_pycompile(self):
        selected_py = os.getenv("TEST_PYTHON_VERSION", "").strip()
        if selected_py and selected_py != "Python 3.8":
            self.skipTest("py_compile validation is only applicable to Python 3.8 payload output")

        py3 = shutil.which("python3")
        self.assertIsNotNone(py3)

        profiles = self._selected_values("TEST_PROFILE", PROFILES)
        crypto_impls = self._selected_values("TEST_CRYPTO_IMPL", tuple(CRYPTO_IMPLEMENTATIONS.keys()))

        for profile in profiles:
            for crypto_impl in crypto_impls:
                with self.subTest(profile=profile, crypto_impl=crypto_impl):
                    resp = self._build_payload(profile, "Python 3.8", CRYPTO_IMPLEMENTATIONS[crypto_impl])
                    self.assertEqual(resp.status, "success", msg=resp.build_stderr)
                    source = resp.payload.decode()
                    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
                        f.write(source)
                        tmp_path = f.name
                    try:
                        py_compile.compile(tmp_path, doraise=True)
                    except py_compile.PyCompileError as e:
                        self.fail(str(e))


if __name__ == "__main__":
    unittest.main()
