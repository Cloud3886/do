import base64
import hashlib

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
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

    def _decrypt(self, data: str) -> str:
        enc = base64.b64decode(data)
        iv = enc[: AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        dnc = cipher.decrypt(enc[AES.block_size :])
        return self._unpad(dnc).decode()

    def _hash(self, data: str) -> str:
        hash_bytes = PBKDF2(data, self.key)
        hash = self._decode_random_bytes(hash_bytes)
        return hash

    @classmethod
    def _generate_key(cls) -> str:
        salt = cls._generate_salt()
        key = cls._decode_random_bytes(salt)
        return key

    @classmethod
    def _generate_salt(cls) -> bytes:
        return get_random_bytes(cls.block_size)

    @classmethod
    def _decode_random_bytes(cls, random: bytes) -> str:
        return base64.b64encode(random).decode()

    def _pad(self, raw: str) -> str:
        s = raw
        bs = self.block_size
        return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

    def _unpad(self, raw: bytes) -> bytes:
        return raw[: -ord(raw[len(raw) - 1 :])]
