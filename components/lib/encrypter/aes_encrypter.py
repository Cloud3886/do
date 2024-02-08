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
        self.key = self._hash_without_salt(secret)

    def _encrypt(self, data: str) -> str:
        raw = self._pad(data)
        iv = random().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        enc = cipher.encrypt(raw.encode(self.encoding))
        return self._encode_bytes(iv + enc)

    def _decrypt(self, data: str) -> str:
        enc = self._decode_bytes(data)
        iv = enc[: AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        dnc = cipher.decrypt(enc[AES.block_size :])
        return self._unpad(dnc).decode(self.encoding)

    def _hash_with_salt(self, data: str, salt: bytes) -> bytes:
        return PBKDF2(data, salt, 32, hmac_hash_module=SHA256)

    def _hash_without_salt(self, data: str) -> bytes:
        return hashlib.sha256(data.encode()).digest()

    def _hash(self, data: str) -> bytes:
        return self._hash_with_salt(data, self.key)

    @classmethod
    def _generate_salt(cls) -> bytes:
        return get_random_bytes(cls.block_size)

    def _pad(self, raw: str) -> str:
        s = raw
        bs = self.block_size
        return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

    def _unpad(self, raw: bytes) -> bytes:
        return raw[: -ord(raw[len(raw) - 1 :])]
