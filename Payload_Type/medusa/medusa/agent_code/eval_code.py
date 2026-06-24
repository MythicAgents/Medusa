    def eval_code(self, task_id, command):
        from contextlib import redirect_stdout, redirect_stderr
        import io
        import json

        f = io.StringIO()

        with redirect_stdout(f), redirect_stderr(f):
            return_value = str(eval(command))

        return json.dumps({
            "result": return_value,
            "stdout": f.getvalue(),
        })