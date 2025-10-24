from typing import Optional

from cryptography.fernet import Fernet


class Cryptography:
    def __init__(self, secret_key: str):
        self.__cipher: Fernet = Fernet(key=secret_key)

    def encrypt(self, key: str) -> str:
        return self.__cipher.encrypt(key.encode("utf-8")).decode("utf-8")

    def decrypt(self, key: str) -> Optional[str]:
        try:
            return self.__cipher.decrypt(key.encode("utf-8")).decode("utf-8")

        except Exception:
            return None
