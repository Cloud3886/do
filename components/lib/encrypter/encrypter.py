import base64
import hashlib
from abc import abstractmethod
from os import urandom
from typing import Protocol


class Encrypter(Protocol):
    _secret: str
    _key: bytes
    encoding = "utf-8"
    block_size = 16
    iterations = 27500
    keysize = 64

    def __init__(self, secret: str) -> None:
        self._secret = secret
        self._key = self._hash_without_salt(secret)

    def encrypt(self, data: str) -> str:
        enc = self._encrypt(data)
        return enc

    def decrypt(self, data: str) -> str:
        data = self._decrypt(data)
        return data

    def hash(self, data: str) -> str:
        hash_bytes = self._hash(data)
        return self._encode_random_bytes(hash_bytes)

    def check_hash(self, data: str, hash: str) -> bool:
        new_hash = self.hash(data)
        return new_hash == hash

    @classmethod
    def generate_key(cls) -> str:
        data = cls._generate_key()
        return data

    @classmethod
    def generate_random_number(cls, stop: int, start: int = 0, step: int = 1) -> int:
        random = cls._generate_random_int((stop - start) // step)
        return start + (random * step)

    @abstractmethod
    def _encrypt(self, data: str) -> str:
        pass

    @abstractmethod
    def _decrypt(self, hash: str) -> str:
        pass

    def _hash(self, data: str) -> bytes:
        return self._hash_with_salt(data, self._key)

    @classmethod
    def _hash_with_salt(cls, data: str, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac(
            "sha256",
            data.encode(cls.encoding),
            salt,
            cls.iterations,
            cls.keysize,
        )

    @classmethod
    def _hash_without_salt(cls, data: str) -> bytes:
        return hashlib.sha256(data.encode(cls.encoding)).digest()

    @classmethod
    def _generate_key(cls) -> str:
        salt = cls._generate_salt()
        key = cls._encode_random_bytes(salt)
        return key

    @classmethod
    def _generate_salt(cls) -> bytes:
        return cls._generate_random(cls.block_size)

    @classmethod
    def _generate_random_int(cls, max: int) -> int:
        """Generate a random number within 0 <= N < max"""

        if max < 2:
            return 0

        def random_int_for_max_in_bits(max: int) -> int:
            size_in_bits = max.bit_length()
            q, r = divmod(size_in_bits, 8)
            size_in_bytes = q + (1 if r > 0 else 0)
            max_in_bits = (1 << size_in_bits) - 1
            random_bytes = urandom(size_in_bytes)
            random_int = int.from_bytes(random_bytes)
            random_int = max_in_bits & random_int
            return random_int

        random_int = max
        while random_int >= max:
            random_int = random_int_for_max_in_bits(max)

        return random_int

    @classmethod
    def _generate_random(cls, size: int) -> bytes:
        return urandom(size)

    @classmethod
    def _encode_random_bytes(cls, data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode(cls.encoding)

    @classmethod
    def _decode_random_bytes(cls, data: bytes | str) -> bytes:
        return base64.urlsafe_b64decode(data)
