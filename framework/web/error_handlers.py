from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.entities.exceptions import (
    DomainError,
    EmailAlreadyUsed,
    InvalidCredentials,
    InvalidToken,
    PermissionDenied,
    TaskNotFound,
)


ERROR_STATUS = {
    EmailAlreadyUsed: 400,
    InvalidCredentials: 401,
    InvalidToken: 401,
    PermissionDenied: 403,
    TaskNotFound: 404,}

def register_error_handlers(app: FastAPI) -> None:
    """Enregistre les gestionnaires d'erreurs personnalisés pour l'application FastAPI."""
    
    for exception_class, status_code in ERROR_STATUS.items():
        def handler(request: Request, exc: DomainError, status_code=status_code):
            """Gestionnaire d'erreur pour les exceptions de domaine."""
            return JSONResponse(
                status_code=status_code,
                content={"detail": str(exc)},
            )
        app.add_exception_handler(exception_class, handler)