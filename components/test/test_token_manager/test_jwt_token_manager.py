import pytest

from components.lib.token_manager.jwt_token_manager import JwtTokenManager
from components.lib.token_manager.token_manager import TokenManager
from components.test._components._testers import ClassTester


class TestJwtTokenManager(ClassTester):
    @pytest.fixture
    def manager(self) -> TokenManager:
        manager = JwtTokenManager("secret")
        return manager

    def test_token_encoder(self, manager: TokenManager):
        sub = "Oh My God"
        token = manager.encode({"sub": sub})

        assert token

    def test_token_decoder(self, manager: TokenManager):
        sub = "Oh My God"
        token = manager.encode({"sub": sub})
        payload = manager.decode(token)
        assert payload["sub"] == sub
