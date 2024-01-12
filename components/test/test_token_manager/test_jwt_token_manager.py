import pytest

from components.lib.token_manager.jwt_token_manager import JwtTokenManager
from components.lib.token_manager.token_manager import TokenManager
from components.test._components._testers import ClassTester


class TestJwtTokenManager(ClassTester):
    @pytest.fixture
    def manager(self) -> TokenManager:
        manager = JwtTokenManager("secret")
        return manager

    def test_payload_generation(self, manager: TokenManager):
        sub = "Oh My God"
        payload = manager.build_payload(sub)

        assert payload["sub"] == sub
        assert "iat" in payload
        assert "exp" in payload

    def test_direct_token_generation(self, manager: TokenManager):
        token = manager.encode({"sub": "Oh My God"})
        payload = manager.decode(token)

        assert payload["sub"] == "Oh My God"
        assert "iat" in payload
        assert "exp" in payload

    def test_token_encoder(self, manager: TokenManager):
        sub = "Oh My God"
        payload = manager.build_payload(sub)
        token = manager.encode(payload)

        assert token

    def test_token_decoder(self, manager: TokenManager):
        sub = "Oh My God"
        token = manager.encode(manager.build_payload(sub))
        payload = manager.decode(token)
        assert payload["sub"] == sub
