    def ps(self, task_id):
        import platform, os
        processes = []
        os_type = platform.system().lower()
        if os_type == 'linux':

            def get_user_id_map():

                user_map = {}
                # get username from uid
                with open("/etc/passwd", "r") as f:
                    passwd = f.readlines()

                for line in passwd:
                    user_line_arr = line.split(":")
                    username = user_line_arr[0].strip()
                    uid = user_line_arr[2].strip()
                    user_map[uid] = username

                return user_map

            # Get the user map
            user_map = get_user_id_map()

            # get list of PIDs by performing a directory listing on /proc
            pids = [pid for pid in os.listdir("/proc") if pid.isdigit()]

            # loop through each PID and output information similar to ps command
            for pid in pids:
                # construct path to status file
                status_path = "/proc/%s/status" % str(pid)

                # read in the status file - bail if process dies before we read the status file
                try:
                    with open(status_path, "r") as f:
                        status = f.readlines()
                except Exception as e:
                    continue

                # construct path to status file
                cmdline_path = "/proc/%s/cmdline" % str(pid)

                # read in the status file
                with open(cmdline_path, "r") as f:
                    cmdline = f.read()
                    cmd_arr = cmdline.split("\x00")
                    cmdline = " ".join(cmd_arr)

                # extract relevant information from status file
                name = ""
                ppid = ""
                uid = ""
                username = ""

                for line in status:
                    if line.startswith("Name:"):
                        name = line.split()[1].strip()
                    elif line.startswith("PPid:"):
                        ppid = line.split()[1].strip()
                    elif line.startswith("Uid:"):
                        uid = line.split()[1].strip()

                # Map the uid to the username
                if uid in user_map:
                    username = user_map[uid]

                process = {"process_id": pid, "parent_process_id": ppid, "user_id": username, "name": name,
                           "bin_path": cmdline}

                processes.append(process)
        elif os_type == 'windows':

            import sys, os.path, ctypes, ctypes.wintypes, re
            from ctypes import create_unicode_buffer, GetLastError

            def _check_bool(result, func, args):
                if not result:
                    raise ctypes.WinError(ctypes.get_last_error())
                return args

            PULONG = ctypes.POINTER(ctypes.wintypes.ULONG)
            ULONG_PTR = ctypes.wintypes.LPVOID
            SIZE_T = ctypes.c_size_t
            NTSTATUS = ctypes.wintypes.LONG
            PVOID = ctypes.wintypes.LPVOID
            PROCESSINFOCLASS = ctypes.wintypes.ULONG

            Psapi = ctypes.WinDLL('Psapi.dll')
            EnumProcesses = Psapi.EnumProcesses
            EnumProcesses.restype = ctypes.wintypes.BOOL
            GetProcessImageFileName = Psapi.GetProcessImageFileNameA
            GetProcessImageFileName.restype = ctypes.wintypes.DWORD

            Kernel32 = ctypes.WinDLL('kernel32.dll')
            OpenProcess = Kernel32.OpenProcess
            OpenProcess.restype = ctypes.wintypes.HANDLE
            CloseHandle = Kernel32.CloseHandle
            CloseHandle.errcheck = _check_bool
            IsWow64Process = Kernel32.IsWow64Process

            WIN32_PROCESS_TIMES_TICKS_PER_SECOND = 1e7

            MAX_PATH = 260
            PROCESS_TERMINATE = 0x0001
            PROCESS_QUERY_INFORMATION = 0x0400

            TOKEN_QUERY = 0x0008
            TOKEN_READ = 0x00020008
            TOKEN_IMPERSONATE = 0x00000004
            TOKEN_QUERY_SOURCE = 0x0010
            TOKEN_DUPLICATE = 0x0002
            TOKEN_ASSIGN_PRIMARY = 0x0001

            ProcessBasicInformation = 0
            ProcessDebugPort = 7
            ProcessWow64Information = 26
            ProcessImageFileName = 27
            ProcessBreakOnTermination = 29

            STATUS_UNSUCCESSFUL = NTSTATUS(0xC0000001)
            STATUS_INFO_LENGTH_MISMATCH = NTSTATUS(0xC0000004).value
            STATUS_INVALID_HANDLE = NTSTATUS(0xC0000008).value
            STATUS_OBJECT_TYPE_MISMATCH = NTSTATUS(0xC0000024).value

            def query_dos_device(drive_letter):
                chars = 1024
                drive_letter = drive_letter
                p = create_unicode_buffer(chars)
                if 0 == Kernel32.QueryDosDeviceW(drive_letter, p, chars):
                    pass
                return p.value

            def create_drive_mapping():
                mappings = {}
                for letter in (chr(l) for l in range(ord('C'), ord('Z') + 1)):
                    try:
                        letter = u'%s:' % letter
                        mapped = query_dos_device(letter)
                        mappings[mapped] = letter
                    except WindowsError:
                        pass
                return mappings

            mappings = create_drive_mapping()
            def normalise_binpath(path):
                match = re.match(r'(^\\Device\\[a-zA-Z0-9]+)(\\.*)?$', path)
                if not match:
                    return f"Cannot convert {path} into a Win32 compatible path"
                if not match.group(1) in mappings:
                    return None
                drive = mappings[match.group(1)]
                if not drive or not match.group(2):
                    return drive
                return drive + match.group(2)

            count = 32
            while True:
                ProcessIds = (ctypes.wintypes.DWORD*count)()
                cb = ctypes.sizeof(ProcessIds)
                BytesReturned = ctypes.wintypes.DWORD()
                if EnumProcesses(ctypes.byref(ProcessIds), cb, ctypes.byref(BytesReturned)):
                    if BytesReturned.value<cb:
                        break
                    else:
                        count *= 2
                else:
                    sys.exit("Call to EnumProcesses failed")

            for index in range(int(BytesReturned.value / ctypes.sizeof(ctypes.wintypes.DWORD))):
                process = {}
                process["process_id"] = ProcessId = ProcessIds[index]
                if ProcessId == 0: continue

                hProcess = OpenProcess(PROCESS_QUERY_INFORMATION, False, ProcessId)
                if hProcess:
                    ImageFileName = (ctypes.c_char*MAX_PATH)()
                    Is64Bit = ctypes.c_int32()
                    IsWow64Process(hProcess, ctypes.byref(Is64Bit))
                    arch = "x86" if Is64Bit.value else "x64"
                    process["architecture"] = arch


                    if GetProcessImageFileName(hProcess, ImageFileName, MAX_PATH)>0:
                        filename = os.path.basename(ImageFileName.value)
                        process["name"] = filename.decode()
                        process["bin_path"] = normalise_binpath(ImageFileName.value.decode())

                    CloseHandle(hProcess)
                processes.append(process)
        elif os_type == 'darwin':
            import ctypes
            import ctypes.util
            import sys
            import pwd

            libc = ctypes.CDLL(ctypes.util.find_library('c'))
            libproc = ctypes.CDLL(ctypes.util.find_library('proc'))

            PROC_ALL_PIDS = 1
            PROC_PIDT_SHORTBSDINFO = 13
            PROC_PIDPATHINFO_MAXSIZE = 4096
            MAXCOMLEN = 16
            CTL_KERN = 1
            KERN_PROCARGS2 = 49

            class ProcBSDShortInfo(ctypes.Structure):
                _fields_ = [
                    ("pbsi_pid", ctypes.c_uint32),                # process id
                    ("pbsi_ppid", ctypes.c_uint32),               # process parent id
                    ("pbsi_pgid", ctypes.c_uint32),               # process perp id
                    ("pbsi_status", ctypes.c_uint32),             # p_stat value
                    ("pbsi_comm", ctypes.c_char * MAXCOMLEN),     # upto 16 chars of proc name
                    ("pbsi_flags", ctypes.c_uint32),              # 64bit; emulated etc
                    ("pbsi_uid", ctypes.c_uint),                  # current uid on process
                    ("pbsi_gid", ctypes.c_uint),                  # current gid on process
                    ("pbsi_ruid", ctypes.c_uint),                 # current ruid on process
                    ("pbsi_rgid", ctypes.c_uint),                 # current tgid on process
                    ("pbsi_svuid", ctypes.c_uint),                # current svuid on process
                    ("pbsi_svgid", ctypes.c_uint),                # current svgid on process
                    ("pbsi_rfu", ctypes.c_uint32),                # reserved
                ]

            proc_count = libc.proc_listpids(PROC_ALL_PIDS, 0, None, 0)
    
            pid_buffer_size = proc_count * ctypes.sizeof(ctypes.c_int)
            pid_buffer = (ctypes.c_int * (pid_buffer_size // ctypes.sizeof(ctypes.c_int)))()
            proc_count = libc.proc_listpids(PROC_ALL_PIDS, 0, ctypes.byref(pid_buffer), pid_buffer_size)
            
            for i in range(proc_count):
                pid = pid_buffer[i]
                if pid == 0:
                    continue  # Skip kernel process

                try:
                    path_buffer = ctypes.create_string_buffer(PROC_PIDPATHINFO_MAXSIZE)
                    ret = libproc.proc_pidpath(pid, path_buffer, PROC_PIDPATHINFO_MAXSIZE)
                    if ret > 0:
                        path = path_buffer.value.decode('utf-8')
                        name = os.path.basename(path)

                    buf = ProcBSDShortInfo()
                    ret = libproc.proc_pidinfo(pid, PROC_PIDT_SHORTBSDINFO, 0, ctypes.byref(buf), ctypes.sizeof(buf))
                    if ret > 0:
                        ppid = buf.pbsi_ppid
                        uid = buf.pbsi_uid
                        
                        if uid == 0:
                            username = "root"
                        else:
                            username = pwd.getpwuid(uid).pw_name if uid else f"unknown({uid})"

                    mib = (ctypes.c_int * 3)()
                    mib[0] = CTL_KERN
                    mib[1] = KERN_PROCARGS2
                    mib[2] = int(pid)

                    buffer_size = ctypes.c_size_t(0)
                    if libc.sysctl(
                        ctypes.byref(mib),
                        ctypes.c_uint32(3),
                        None,
                        ctypes.byref(buffer_size),
                        None,
                        ctypes.c_size_t(0)
                    ) == 0:
                        argc_buffer = (ctypes.c_ubyte * buffer_size.value)()
                        if libc.sysctl(
                            ctypes.byref(mib),
                            ctypes.c_uint32(3),
                            ctypes.byref(argc_buffer),
                            ctypes.byref(buffer_size),
                            None,
                            ctypes.c_size_t(0)
                        ) == 0:
                            argc = int.from_bytes(bytearray(argc_buffer[:4]), sys.byteorder) + 1
                            args_data = bytearray(argc_buffer[4:])

                            arguments = []
                            current = 0
                            for idx in range(argc):
                                # Skip null bytes
                                while current < len(args_data) and args_data[current] == 0:
                                    current += 1
                                if current >= len(args_data):
                                    break
                                try:
                                    next_null = args_data.index(0, current)
                                except ValueError:
                                    next_null = len(args_data)
                                arg = args_data[current:next_null].decode('utf-8', errors='ignore')
                                if idx != 0:
                                    arguments.append(arg)
                                current = next_null + 1

                            command_line = ' '.join(arguments)

                    processes.append({
                        "process_id": pid,
                        "parent_process_id": ppid,  
                        "user_id": uid,  
                        "name": name,  
                        "bin_path": path,
                        "command_line": command_line,
                        "user": username
                    })
                except Exception as e:
                    print(f"Error processing PID {pid}: {e}")

        else:
            return f"{os.name} is not supported"

        task = [task for task in self.taskings if task["task_id"] == task_id]
        task[0]["processes"] = processes
        return json.dumps({ "processes": processes })
