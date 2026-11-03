class DomainError(Exception):
    """Base class for domain errors."""
    message = "Erreur metier"

def __init__(self, message: str | None = None):
    super().__init__(message or self.message)

class EmailAlreadyUsed(DomainError):
    message = "L'email est déjà utilisé"

class InvalidCredentials(DomainError):
    message = "Identifiants invalides"


class InvalidToken(DomainError):
    message = "Token invalide ou expiré"


class TaskNotFound(DomainError):
    message = "Tâche non trouvée"

class UnauthorizedAccess(DomainError):
    message = "Accès non autorisé"