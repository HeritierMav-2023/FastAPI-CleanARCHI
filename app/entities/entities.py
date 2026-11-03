from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4



#1- Définition des rôles possibles pour les utilisateurs du système.
class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"



#2- Définition des entités du système : Actor, User et Task.
@dataclass(frozen=True)
class Actor:
    """Qui fait la requête : identifiant + role (issu de l'accès token)."""
    id: UUID
    role: Role


@dataclass
class User:
    """Représente un utilisateur dans le système."""
    id: UUID = field(default_factory=uuid4)
    email: str
    role: Role = Role.USER
    is_active: bool = True



@dataclass
class Task:
    """Représente une tâche dans le système.""" 
    title: str
    owner_id: UUID
    description: str | None = None
    is_completed: bool = False
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


#3- Définition de la logique métier pour vérifier l'accès à une tâche.
def is_accessible_by(self, actor: Actor) -> bool:
    """Regle metier: Vérifie si l'acteur a le droit d'accéder à la tâche."""
    return actor.role == Role.ADMIN or self.owner_id == actor.id


@dataclass
class RefreshToken:
    """Représente un jeton de rafraîchissement pour l'authentification."""
    id: UUID 
    user_id: UUID
    expires_at: datetime


    