from fastapi import Response

from app.use_cases.gateways import TokenPair
from framework.config import settings

ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"

def set_auth_cookies(response: Response, token_pair: TokenPair) -> None:
    """Définit les cookies d'authentification pour l'accès et le rafraîchissement."""
    common = dict(
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite
        )
    response.set_cookie(
        ACCESS_COOKIE,
        token_pair.access_token,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
        **common
    )
    response.set_cookie(
        REFRESH_COOKIE,
        token_pair.refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/",
        **common
    )


def clear_auth_cookies(response: Response) -> None:
    """Supprime les cookies d'authentification."""
    response.delete_cookie(ACCESS_COOKIE, path="/")
    response.delete_cookie(REFRESH_COOKIE, path="/auth")

    