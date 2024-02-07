from abc import abstractmethod
from typing import Any, Protocol


class Encrypter(Protocol):
    _secret: str

    def __init__(self, secret: str) -> None:
        self._secret = secret

    def encrypt(self, data: str) -> str:
        token = self._encrypt(data)
        return token

    def decrypt(self, hash: str) -> str:
        data = self._decrypt(hash)
        return data

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

    @classmethod
    @abstractmethod
    def _generate_key(cls) -> str:
        pass
