from typing import Annotated

from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session as SQLAlchemySession
from app.use_cases.gateways import RefreshTokenRepository, TaskRepository, TokenService, UserRepository
from app.use_cases.auth import LoginUser, LogoutUser, RefreshSession, RegisterUser
from app.use_cases.tasks import CreateTask, DeleteTask,ListMyTasks, ListAllTasks, GetTask,UpdateTask
from framework.config import settings
from app.entities.entities import Actor, Role
from app.entities.exceptions import InvalidToken
from app.interface_adapters.gateways.db.repositories import (
    SqlAlchemyRefreshTokenRepository, SqlAlchemyTaskRepository, SqlAlchemyUserRepository)
from framework.db.session import get_session
from app.interface_adapters.gateways.security.jwt_service import JWtTokenService
from app.interface_adapters.gateways.security.password import Argon2PasswordHasher

#--Objets sans etat : crees une seule  fois 
_hasher = Argon2PasswordHasher()
_tokens = JWtTokenService(
    secret_key = settings.jwt_secret_key,
    algorithm = settings.jwt_algorithm,
    access_token_expire_minutes = settings.access_token_expire_minutes,
    refresh_token_expire_days = settings.refresh_token_expire_days
)

def get_token_service() -> TokenService:
    """Fournit une instance de TokenService."""
    return _tokens


#--Repositories : lies a la session de la requete
def get_user_repo(s: Annotated[SQLAlchemySession, Depends(get_session)]) -> UserRepository: 
    """Fournit une instance de UserRepository liée à la session de la requête."""
    return SqlAlchemyUserRepository(s)

def get_task_repo(s: Annotated[SQLAlchemySession, Depends(get_session)]) -> TaskRepository:
    """Fournit une instance de TaskRepository liée à la session de la requête."""
    return SqlAlchemyTaskRepository(s)

def get_refresh_token_repo(s: Annotated[SQLAlchemySession, Depends(get_session)]) -> RefreshTokenRepository:
    """Fournit une instance de RefreshTokenRepository liée à la session de la requête."""
    return SqlAlchemyRefreshTokenRepository(s)

#-- Cas d'usage d'authentification : lies a la session de la requete
def get_register_user(
    users = Depends(get_user_repo)
):
    """Fournit une instance de RegisterUser."""
    return RegisterUser(users, _hasher)

def get_login_user(
    users = Depends(get_user_repo),
    refresh = Depends(get_refresh_token_repo),
):
    """Fournit une instance de LoginUser."""
    return LoginUser(users, refresh, _hasher, _tokens)

def get_logout_user(
    refresh = Depends(get_refresh_token_repo),
):
    """Fournit une instance de LogoutUser."""
    return LogoutUser(refresh, _tokens)   

def get_refresh_session(
    users = Depends(get_user_repo),
    refresh = Depends(get_refresh_token_repo),
):
    """Fournit une instance de RefreshSession."""
    return RefreshSession(users, refresh, _tokens)

#-- Cas d'usage des taches 
def get_create_task(
    tasks = Depends(get_task_repo)
):
    """Fournit une instance de CreateTask."""
    return CreateTask(tasks)


def get_list_my_tasks(
    tasks = Depends(get_task_repo)
):
    """Fournit une instance de ListMyTasks."""
    return ListMyTasks(tasks)

def get_list_all_tasks(
    tasks = Depends(get_task_repo)
):
    """Fournit une instance de ListAllTasks."""
    return ListAllTasks(tasks)

def get_get_task(
    tasks = Depends(get_task_repo)
):
    """Fournit une instance de GetTask."""
    return GetTask(tasks)  

def get_update_task(
    tasks = Depends(get_task_repo)
):
    """Fournit une instance de UpdateTask."""
    return UpdateTask(tasks)

def get_delete_task(
    tasks = Depends(get_task_repo)
):
    """Fournit une instance de DeleteTask."""
    return DeleteTask(tasks)  

# -- Authentification et roles --
def get_current_actor(
    access_token: Annotated[str | None, Cookie()] = None,
    token_service: TokenService = Depends(get_token_service)
) -> Actor:
    """Récupère l'acteur actuel à partir du token d'accès."""
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token is missing")
    try:
        return token_service.decode_access_token(access_token)
    except InvalidToken:
        raise HTTPException(status_code=401, detail="Invalid access token")


def require_role(*roles: Role):
    """Dépendance FastAPI pour vérifier le rôle de l'acteur actuel."""
    def role_checker(actor: Actor = Depends(get_current_actor))-> Actor:
        if actor.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return actor
    return role_checker
