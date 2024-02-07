import pytest

from components.lib.encrypter.aes_encrypter import AesEncrypter
from components.lib.encrypter.encrypter import Encrypter
from components.test._components._testers import ClassTester


class TestAesEncrypter(ClassTester):
    @pytest.fixture
    def encrypter(self) -> Encrypter:
        encrypter = AesEncrypter("secret")
        return encrypter

    def test_token_encoder(self, encrypter: Encrypter):
        sub = "Oh My God"
        hash = encrypter.encrypt(sub)
        assert hash

    def test_token_decoder(self, encrypter: Encrypter):
        sub = "Oh My God"
        hash = encrypter.encrypt(sub)
        payload = encrypter.decrypt(hash)
        assert payload == sub

    def test_key_generator(self):
        key = AesEncrypter.generate_key()
        assert key

    def test_hash_generator(self, encrypter: Encrypter):
        sub = "Oh My God"
        hash = encrypter.hash(sub)
        assert hash

    def test_hash_check(self, encrypter: Encrypter):
        sub = "Oh My God"
        hash = encrypter.hash(sub)
        assert encrypter.check_hash(sub, hash)
