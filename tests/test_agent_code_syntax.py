import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
AGENT_CODE_PATH = ROOT / "Payload_Type" / "medusa" / "medusa" / "agent_code"

# Each agent_code command file is a class-method fragment (an indented `def`
# meant to be spliced into the agent class at build time), so wrapping it in a
# throwaway class body makes it a syntactically valid module for compilation.
CLASS_WRAPPER = "class _SyntaxCheck(object):\n"

# `.py` files are python-version agnostic and compile under either interpreter.
# `.py2`/`.py3` files are validated only by their matching interpreter, since
# each may contain syntax the other version cannot parse. CI runs this test
# under both Python 2 and Python 3 to cover every fragment.
if sys.version_info[0] == 2:
    FRAGMENT_SUFFIXES = ("py", "py2")
else:
    FRAGMENT_SUFFIXES = ("py", "py3")


def discover_command_fragments(suffixes):
    fragments = []
    for path in sorted(AGENT_CODE_PATH.glob("*")):
        if path.is_file() and path.name.rsplit(".", 1)[-1] in suffixes:
            fragments.append(path)
    return fragments


def _make_compile_test(fragment):
    def test(self):
        wrapped = CLASS_WRAPPER + fragment.read_text()
        try:
            compile(wrapped, fragment.name, "exec")
        except SyntaxError as e:
            self.fail("Syntax error in {}: {}".format(fragment.name, e))

    test.__doc__ = "syntax check: {}".format(fragment.name)
    return test


class TestAgentCodeSyntax(unittest.TestCase):
    def test_command_fragments_discovered(self):
        fragments = discover_command_fragments(FRAGMENT_SUFFIXES)
        self.assertTrue(fragments, "No agent_code command fragments were discovered")


def _attach_fragment_tests():
    # Generate one test method per fragment so each file shows up as its own
    # result line in verbose/debug output (e.g. test_cat_py, test_ls_py3).
    for fragment in discover_command_fragments(FRAGMENT_SUFFIXES):
        name = "test_" + fragment.name.replace(".", "_")
        setattr(TestAgentCodeSyntax, name, _make_compile_test(fragment))


_attach_fragment_tests()


if __name__ == "__main__":
    unittest.main()
