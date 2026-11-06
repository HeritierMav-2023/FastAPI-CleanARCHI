from argon2 import PasswordHasher as _Argon2
from argon2.exceptions import VerifyMismatchError, InvalidHashError

from app.use_cases.gateways import PasswordHasher


class Argon2PasswordHasher(PasswordHasher):
    """Implémentation de PasswordHasher utilisant Argon2."""
    
    def __init__(self):
        self._hasher = _Argon2()

    def hash(self, password: str) -> str:
        """Hash le mot de passe en utilisant Argon2."""
        return self._hasher.hash(password)

    def verify(self, password: str, hashed_password: str) -> bool:
        """Vérifie si le mot de passe correspond au hash Argon2."""
        try:
            return self._hasher.verify(hashed_password, password)
        except (VerifyMismatchError, InvalidHashError):
            return False

