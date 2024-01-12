from typing import Any

import jwt

from .token_manager import TokenManager


class JwtTokenManager(TokenManager):
    def _encode(self, payload: dict[str, Any]) -> str:
        return jwt.encode(payload, self._secret, algorithm=self.algorithm)

    def _decode(self, token: str) -> dict[str, Any]:
        return jwt.decode(token, self._secret, algorithms=[self.algorithm])
