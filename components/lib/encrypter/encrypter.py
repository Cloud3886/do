import base64
from abc import abstractmethod
from typing import Any, Protocol


class Encrypter(Protocol):
    _secret: str
    encoding: str = "utf-8"

    def __init__(self, secret: str) -> None:
        self._secret = secret

    def encrypt(self, data: str) -> str:
        enc = self._encrypt(data)
        return enc

    def decrypt(self, data: str) -> str:
        data = self._decrypt(data)
        return data

    def hash(self, data: str) -> str:
        hash_bytes = self._hash(data)
        return self._encode_bytes(hash_bytes)

    def check_hash(self, data: str, hash: str) -> bool:
        new_hash = self.hash(data)
        return new_hash == hash

    @classmethod
    def generate_key(cls) -> str:
        data = cls._generate_key()
        return data

    @classmethod
    def _generate_key(cls) -> str:
        salt = cls._generate_salt()
        key = cls._encode_bytes(salt)
        return key

    @classmethod
    def _encode_bytes(cls, data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode(cls.encoding)

    @classmethod
    def _decode_bytes(cls, data: bytes | str) -> bytes:
        return base64.urlsafe_b64decode(data)

    @abstractmethod
    def _encrypt(self, data: str) -> str:
        pass

    @abstractmethod
    def _decrypt(self, hash: str) -> str:
        pass

    @abstractmethod
    def _hash(self, data: str) -> bytes:
        pass

    @classmethod
    @abstractmethod
    def _generate_salt(cls) -> bytes:
        pass
