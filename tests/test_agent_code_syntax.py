import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENT_CODE_PATH = os.path.join(ROOT, "Payload_Type", "medusa", "medusa", "agent_code")

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
    for name in sorted(os.listdir(AGENT_CODE_PATH)):
        path = os.path.join(AGENT_CODE_PATH, name)
        if os.path.isfile(path) and name.rsplit(".", 1)[-1] in suffixes:
            fragments.append(path)
    return fragments


def _read_file(path):
    with open(path, "r") as f:
        return f.read()


def _make_compile_test(fragment):
    fragment_name = os.path.basename(fragment)

    def test(self):
        wrapped = CLASS_WRAPPER + _read_file(fragment)
        try:
            compile(wrapped, fragment_name, "exec")
        except SyntaxError as e:
            self.fail("Syntax error in {}: {}".format(fragment_name, e))

    test.__doc__ = "syntax check: {}".format(fragment_name)
    return test


class TestAgentCodeSyntax(unittest.TestCase):
    def test_command_fragments_discovered(self):
        fragments = discover_command_fragments(FRAGMENT_SUFFIXES)
        self.assertTrue(fragments, "No agent_code command fragments were discovered")


def _attach_fragment_tests():
    # Generate one test method per fragment so each file shows up as its own
    # result line in verbose/debug output (e.g. test_cat_py, test_ls_py3).
    for fragment in discover_command_fragments(FRAGMENT_SUFFIXES):
        name = "test_" + os.path.basename(fragment).replace(".", "_")
        setattr(TestAgentCodeSyntax, name, _make_compile_test(fragment))


_attach_fragment_tests()


if __name__ == "__main__":
    unittest.main()
