from abc import ABC, abstractmethod
from uuid import UUID
from dataclasses import dataclass, field
from datetime import datetime, timezone
from app.entities.entities import Actor, RefreshToken, RefreshToken, Task, User


#---------------Gateways de persistance-----------------
#--------------------------------------------------------

#1- classe abstraite pour le repository des utilisateurs.
class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None:...

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:...


#2- classe abstraite pour le repository des tâches.
class TaskRepository(ABC):
    @abstractmethod
    def add(self, task: Task) -> Task | None:...

    @abstractmethod
    def list_by_owner(self, owner_id: UUID) -> list[Task]:...

    @abstractmethod
    def list_all(self) -> list[Task]:...

    @abstractmethod
    def update(self, task: Task) -> Task | None:...

    @abstractmethod
    def delete(self, task_id: UUID) -> bool:...

#3- classe abstraite pour le repository des jetons de rafraîchissement.
class RefreshTokenRepository(ABC):
    @abstractmethod
    def add(self, refresh_token: RefreshToken) -> RefreshToken | None:...

    @abstractmethod
    def get(self, token_id: UUID) -> RefreshToken | None:...

    @abstractmethod
    def revoke(self, token_id: UUID) -> None:...

    @abstractmethod
    def revoke_all_for_user(self, user_id: UUID) -> None:...


#-----------------Gateways de  securite-----------------
#--------------------------------------------------------

#1- classe abstraite pour le service de hachage des mots de passe.
class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, password: str) -> str:...

    @abstractmethod
    def verify(self, password: str, hashed_password: str) -> bool:...


#2- classe autorisant la gestion des tokens JWT pour l'authentification et l'autorisation.
@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str

#3- classe abstraite refresh token claims
@dataclass(frozen=True)
class RefreshClaims:
    user_id: UUID
    jti: UUID


#4- classe abstraite pour le service de gestion des tokens JWT.
class TokenService(ABC):
    @abstractmethod
    def create_access_token(self, user: User) -> str:...

    @abstractmethod
    def create_refresh_token(self, user: User) -> tuple[str, UUID,datetime]:...

    @abstractmethod
    def decode_access_token(self, token: str) -> Actor:...

    @abstractmethod
    def decode_refresh_token(self, token: str) -> RefreshClaims:...
