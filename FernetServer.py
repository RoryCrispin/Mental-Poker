from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


class FernetServer():
    def __init__(self, shared_key):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'salt',
            iterations=100000,
            backend=default_backend())
        self.key = base64.urlsafe_b64encode(kdf.derive(shared_key))

        self.f = Fernet(self.key)

    def encrypt_message(self, message):
        return self.f.encrypt(message.encode())

    def decrypt_message(self, cipher):
        return self.f.decrypt(cipher).decode()
