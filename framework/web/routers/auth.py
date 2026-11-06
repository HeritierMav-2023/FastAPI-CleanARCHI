from fastapi import APIRouter, Cookie, Depends, HTTPException, Response

from app.use_cases.auth import RegisterUser, LoginUser, LogoutUser, RefreshSession
from app.entities.entities import Actor
from app.entities.exceptions import InvalidToken
from framework.web.cookies import clear_auth_cookies, set_auth_cookies
from framework.web.dependencies import (
    get_current_actor,
    get_login_user,
    get_logout_user,
    get_refresh_session,
    get_register_user,
    get_user_repo,
)
from app.interface_adapters.schemas import LoginRequest, RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(body: RegisterRequest, 
             register_user: RegisterUser = Depends(get_register_user)):
    """Enregistre un nouvel utilisateur."""
    user = register_user.execute(body.email, body.password)
    return UserResponse.model_validate(user)

@router.post("/login")
def login(body: LoginRequest, 
          response: Response,
          login_user: LoginUser = Depends(get_login_user)):
    """Authentifie un utilisateur et retourne un jeton d'accès et un jeton de rafraîchissement."""
    token_pair = login_user.execute(body.email, body.password)
    set_auth_cookies(response, token_pair)
    return {"access_token": token_pair.access_token}

@router.post("/refresh")
def refresh(response: Response,
            refresh_token: str | None = Cookie(default=None),
            use_case: RefreshSession = Depends(get_refresh_session)):
    """Rafraîchit le jeton d'accès en utilisant le jeton de rafraîchissement."""
    if not refresh_token:
        raise InvalidToken("Refresh token is missing.")
    pair = use_case.execute(refresh_token)
    set_auth_cookies(response, pair)
    return {"message": "Session renouvellée."}


@router.post("/logout")
def logout(response: Response,
           refresh_token: str | None = Cookie(default=None),
           logout_user: LogoutUser = Depends(get_logout_user)):
    """Déconnecte un utilisateur en révoquant son jeton de rafraîchissement."""
    if refresh_token:
        logout_user.execute(refresh_token)
    clear_auth_cookies(response)
    return {"message": "Déconnecté avec succès."}

@router.get("/me", response_model=UserResponse)
def get_current_user(
    actor: Actor = Depends(get_current_actor),
    users=Depends(get_user_repo),
):
    """Récupère les informations de l'utilisateur actuellement authentifié."""
    user = users.get_by_id(actor.id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)