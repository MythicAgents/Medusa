class medusa:
    def encrypt(self, data):
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.primitives import hashes, hmac, padding
        from cryptography.hazmat.backends import default_backend

        if not self.agent_config["enc_key"]["value"] == "none" and len(data)>0:
            key = base64.b64decode(self.agent_config["enc_key"]["enc_key"])
            iv = os.urandom(16)

            backend = default_backend()
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend)
            encryptor = cipher.encryptor()

            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(data)
            padded_data += padder.finalize()

            ct = encryptor.update(padded_data) + encryptor.finalize()

            h = hmac.HMAC(key, hashes.SHA256(), backend)
            h.update(iv + ct)
            hmac = h.finalize()

            output = iv + ct + hmac
            return output
        else:
            return data

    def decrypt(self, data):
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.primitives import hashes, hmac, padding
        from cryptography.hazmat.backends import default_backend

        if not self.agent_config["enc_key"]["value"] == "none":
            if len(data)>0:
                backend = default_backend()

                key = base64.b64decode(self.agent_config["enc_key"]["dec_key"])
                uuid = data[:36]
                iv = data[36:52]
                ct = data[52:-32]
                received_hmac = data[-32:]

                h = hmac.HMAC(key, hashes.SHA256(), backend)
                h.update(iv + ct)
                hmac = h.finalize()

                if base64.b64encode(hmac) == base64.b64encode(received_hmac):
                    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend)
                    decryptor = cipher.decryptor()
                    pt = decryptor.update(ct) + decryptor.finalize()
                    unpadder = padding.PKCS7(128).unpadder()
                    decrypted_data = unpadder.update(pt)
                    decrypted_data += unpadder.finalize()
                    return (uuid+decrypted_data).decode()
                else: return ""
            else: return ""
        else:
            return data.decode()
