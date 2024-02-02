from abc import abstractmethod
from typing import Any, Protocol


class TokenManager(Protocol):
    _secret: str
    algorithm: str

    def __init__(
        self,
        secret: Any,
        algorithm: str | None = None,
    ) -> None:
        self._secret = secret
        self.algorithm = algorithm or "HS256"

    def encode(self, payload: dict[str, Any]) -> str:
        token = self._encode(payload)
        return token

    def decode(self, token: str) -> dict[str, Any]:
        data = self._decode(token)
        return data

    @abstractmethod
    def _encode(self, payload: dict[str, Any]) -> str:
        pass

    @abstractmethod
    def _decode(self, token: str) -> dict[str, Any]:
        pass
