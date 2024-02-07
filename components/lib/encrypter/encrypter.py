from abc import abstractmethod
from typing import Any, Protocol


class Encrypter(Protocol):
    _secret: str

    def __init__(self, secret: str) -> None:
        self._secret = secret

    def encrypt(self, data: str) -> str:
        enc = self._encrypt(data)
        return enc

    def decrypt(self, data: str) -> str:
        data = self._decrypt(data)
        return data

    def hash(self, data: str) -> str:
        data = self._hash(data)
        return data

    def check_hash(self, data: str, hash: str) -> bool:
        new_hash = self.hash(data)
        return new_hash == hash

    @classmethod
    def generate_key(cls) -> str:
        data = cls._generate_key()
        return data

    @abstractmethod
    def _encrypt(self, data: str) -> str:
        pass

    @abstractmethod
    def _decrypt(self, hash: str) -> str:
        pass

    @abstractmethod
    def _hash(self, data: str) -> str:
        pass

    @classmethod
    @abstractmethod
    def _generate_key(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def _generate_salt(cls) -> bytes:
        pass
