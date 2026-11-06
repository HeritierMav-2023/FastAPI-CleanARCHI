from app.use_cases.gateways import (PasswordHasher, RefreshTokenRepository, UserRepository, TokenService, TokenPair)
from app.entities.entities import User, RefreshToken
from app.entities.exceptions import EmailAlreadyUsed, InvalidCredentials, InvalidToken


#-----------------Use Cases d'authentification-----------------
#--------------------------------------------------------

#1- methode issue_token_pair: Génère un nouveau pair de tokens (access + refresh) pour l'utilisateur donné.
def _issue_token_pair(
        user: User, token_service: TokenService,
          refresh_token_repo: RefreshTokenRepository
          ) -> TokenPair:
    """Génère un nouveau pair de tokens (access + refresh) pour l'utilisateur donné."""

    access_token = token_service.create_access_token(user)
    refresh,jti,expires_at = token_service.create_refresh_token(user)

    refresh_token_repo.add(
        RefreshToken(id=jti, user_id=user.id, expires_at=expires_at)
        )
    return TokenPair(access_token=access_token, refresh_token=refresh)


#2- Use case pour l'enregistrement d'un nouvel utilisateur.
class RegisterUser:
    
    """Use case pour l'enregistrement d'un nouvel utilisateur."""
    def __init__(self, user_repo: UserRepository, password_hasher: PasswordHasher):
        self.user_repo = user_repo
        self.password_hasher = password_hasher

    def execute(self, email: str, password: str) -> User:
        """Enregistre un nouvel utilisateur avec l'email et le mot de passe fournis."""
        if self.user_repo.get_by_email(email):
            raise EmailAlreadyUsed()

        user = User(email=email, hashed_password=self.password_hasher.hash(password))
        return self.user_repo.add(user)
        

class LoginUser:
    def __init__(self, users,refresh_repo,hasher, token_service):
        self.users = users
        self.refresh_repo = refresh_repo
        self.hasher = hasher
        self.token_service = token_service

    def execute(self, email: str, password: str) -> TokenPair:
        """Authentifie un utilisateur et retourne un pair de tokens (access + refresh)."""
        user = self.users.get_by_email(email.lower())

        if user is None or not user.is_active or not self.hasher.verify(password, user.hashed_password):
            raise InvalidCredentials()

        return _issue_token_pair(user, self.token_service, self.refresh_repo)


# Use case pour rafraîchir la session d'un utilisateur en utilisant un jeton de rafraîchissement.
class RefreshSession:
    def __init__(self, users, refresh_repo, token_service):
        self.users = users
        self.refresh_repo = refresh_repo
        self.token_service = token_service

    def execute(self, refresh_token: str) -> TokenPair:
        """Rafraîchit la session de l'utilisateur en utilisant le jeton de rafraîchissement fourni."""
        claims = self.token_service.decode_refresh_token(refresh_token)
        stored = self.refresh_repo.get(claims.jti)

        if stored is None :
            raise InvalidToken()

        if stored.revoked:
            # Reutilisation d'un token révoqué, ce qui est une violation de sécurité.
            self.refresh_repo.revoke_all_for_user(stored.user_id)
            raise InvalidToken()

        user = self.users.get_by_id(claims.user_id)
        if user is None or not user.is_active:
            raise InvalidToken()
        self.refresh_repo.revoke(stored.id)    #Rotation du token de rafraîchissement après utilisation.
        
        return _issue_token_pair(user, self.token_service, self.refresh_repo)

class LogoutUser:
    def __init__(self, refresh_repo, tokens):
        self.refresh_repo = refresh_repo
        self.tokens = tokens

    def execute(self, refresh_token: str) -> None:
      try:
          claims = self.tokens.decode_refresh_token(refresh_token)

      except InvalidToken:
          return  # Si le token est invalide, on ne fait rien (pas d'erreur).
      self.refresh_repo.revoke(claims.jti)  # Révoque le token de rafraîchissement pour déconnecter l'utilisateur.

      
    
