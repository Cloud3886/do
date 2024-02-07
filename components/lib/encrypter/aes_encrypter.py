import base64
import hashlib

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Random import new as random

from .encrypter import Encrypter


class AesEncrypter(Encrypter):
    block_size = AES.block_size

    def __init__(self, secret: str) -> None:
        super().__init__(secret)
        self.key = hashlib.sha256(secret.encode()).digest()

    def _encrypt(self, data: str) -> str:
        raw = self._pad(data)
        iv = random().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        enc = cipher.encrypt(raw.encode())
        return base64.b64encode(iv + enc).decode("utf-8")

    def _decrypt(self, hash: str) -> str:
        enc = base64.b64decode(hash)
        iv = enc[: AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        dnc = cipher.decrypt(enc[AES.block_size :])
        return self._unpad(dnc).decode()

    @classmethod
    def _generate_key(cls) -> str:
        urandom = get_random_bytes(cls.block_size)
        key = base64.b64encode(urandom).decode("utf-8")
        return key

    def _pad(self, raw: str) -> str:
        s = raw
        bs = self.block_size
        return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

    def _unpad(self, raw: bytes) -> bytes:
        return raw[: -ord(raw[len(raw) - 1 :])]
