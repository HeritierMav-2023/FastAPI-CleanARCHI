from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, ConfigDict

from app.entities.entities import Role


class RegisterRequest(BaseModel):
    """Schéma pour la requête d'enregistrement d'un utilisateur."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Schéma pour la requête de connexion d'un utilisateur."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    """Schéma pour la réponse contenant les informations d'un utilisateur."""
    id: UUID
    email: EmailStr
    role: Role

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    """Schéma pour la requête de création d'une tâche."""
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1024)


class TaskUpdate(BaseModel):
    """Schéma pour la requête de mise à jour d'une tâche."""
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    is_completed: bool | None = Field(default=None)

    
class TaskResponse(BaseModel):
    """Schéma pour la réponse contenant les informations d'une tâche."""
    id: UUID
    title: str
    description: str | None
    is_completed: bool
    owner_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



