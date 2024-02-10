from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2

from .encrypter import Encrypter


class AesEncrypter(Encrypter):
    block_size = AES.block_size

    def __init__(self, secret: str) -> None:
        super().__init__(secret)

    def _encrypt(self, data: str) -> str:
        raw = self._pad(data)
        iv = self._generate_salt()
        cipher = AES.new(self._key, AES.MODE_CBC, iv)
        enc = cipher.encrypt(raw.encode(self.encoding))
        return self._encode_random_bytes(iv + enc)

    def _decrypt(self, data: str) -> str:
        enc = self._decode_random_bytes(data)
        iv = enc[: AES.block_size]
        cipher = AES.new(self._key, AES.MODE_CBC, iv)
        dnc = cipher.decrypt(enc[AES.block_size :])
        return self._unpad(dnc).decode(self.encoding)

    def _hash_with_salt(self, data: str, salt: bytes) -> bytes:
        return PBKDF2(
            data,
            salt,
            self.keysize,
            self.iterations,
            hmac_hash_module=SHA256,
        )

    def _pad(self, raw: str) -> str:
        s = raw
        bs = self.block_size
        return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

    def _unpad(self, raw: bytes) -> bytes:
        return raw[: -ord(raw[len(raw) - 1 :])]
