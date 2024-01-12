from datetime import datetime, timedelta
from typing import Any

import jwt


class JwtTokenManager:
    def __init__(
        self,
        secret: Any,
        algorithm: str | None = None,
    ) -> None:
        self.__secret = secret
        self.algorithm = algorithm or "HS256"

    @staticmethod
    def build_payload(
        sub: str,
        expire_in_mins: int = 24 * 60,
    ) -> dict[str, Any]:
        return {
            "sub": sub,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=expire_in_mins),
        }

    def encode(self, payload: dict[str, Any]) -> str:
        payload = self._ensure_req_fields(payload)
        token = jwt.encode(payload, self.__secret, algorithm=self.algorithm)
        return token

    def decode(self, token: str) -> dict[str, Any]:
        data = jwt.decode(token, self.__secret, algorithms=[self.algorithm])
        return data

    def _ensure_req_fields(self, payload: dict[str, Any]) -> dict[str, Any]:
        payload = self._ensure_key(
            payload, "exp", datetime.utcnow() + timedelta(days=1)
        )
        payload = self._ensure_key(payload, "iat", datetime.utcnow())

        return payload

    @staticmethod
    def _ensure_key(payload: dict[str, Any], key: str, value: Any) -> dict[str, Any]:
        if not payload.get(key):
            payload[key] = value

        return payload
