
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from cryptography.hazmat.primitives.serialization\
    import load_pem_parameters, load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.serialization import Encoding,\
    ParameterFormat, PublicFormat

from cryptography.hazmat.backends import default_backend


class DHServer(object):
    def __init__(self):
        super().__init__()
        # This example DH server uses a known safe prime, or can generate its
        # own if the PEM file is not available.
        # The safe prime used here is ffdhe2048, described here:
        # https://tools.ietf.org/html/rfc7919#appendixA.1
        # There is nothing strictly wrong with generating your own prime,
        # but this one is well tested.

        import os.path
        pem_path = os.path.join(os.path.dirname(__file__), 'dh_params.pem')
        if not os.path.isfile(pem_path):
            # No PEM file available, generate a new prime of 2048 bits.
            parameters = dh.generate_parameters(
                generator=2, key_size=2048, backend=default_backend())
            s = parameters.parameter_bytes(Encoding.PEM, ParameterFormat.PKCS3)
            with open('dh_params.pem', 'wb') as outfile:
                outfile.write(s)
        # Load PEM file  a standard format for cryptographic
        # keys and numbers.
        with open(pem_path, 'r') as f:
            self.pem_data = f.read().encode("UTF8")
        self.parse_parameters(self.pem_data.decode())

    def encrypt_message(self, message):
        if not self._shared_key:
            return None
        message = message.encode()
        from os import urandom
        nonce = urandom(16)

        cipher = Cipher(
            algorithms.AES(self._shared_key),
            modes.CTR(nonce),
            backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(bytes([b + 12 % 255 for b in message
                                             ])) + encryptor.finalize()
        return nonce + ciphertext

    def parse_parameters(self, params):
        # TODO: Use proper library serialisation
        # https://cryptography.io/en/latest/hazmat/primitives/asymmetric/serialization/#cryptography.hazmat.primitives.serialization.load_pem_parameters
        bytestring = params.encode()
        self.parameters = load_pem_parameters(
            data=bytestring, backend=default_backend())

    # Return DH parameters (prime and generator)
    def get_serialised_parameters(self):
        return self.pem_data.decode()

    # Generate a new private key (a random number) and produce the public
    # key based on this and the parameters.
    def get_public_key(self):
        self.privatekey = self.parameters.generate_private_key()
        self.public_key = self.privatekey.public_key()
        return self.public_key

    # Receive another public key as part of a handshake, and use it to
    # calculate a share secret
    def submit_public_key(self, pk):
        if pk == None:
            return

        self._pre_master_secret = self.privatekey.exchange(pk)

        # Derive the key
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'g53sec',
            backend=default_backend())

        self._shared_key = hkdf.derive(self._pre_master_secret)
