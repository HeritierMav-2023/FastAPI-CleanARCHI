from datetime import datetime, timedelta, timezone
import token
from uuid import UUID, uuid4
import jwt

from app.use_cases.gateways import RefreshClaims, TokenService
from app.entities.entities import Actor, Role, User
from app.entities.exceptions import InvalidToken


class JWtTokenService(TokenService):
    """Implémentation de TokenService utilisant JWT pour la gestion des tokens."""


    def __init__(self, secret_key: str, algorithm: str, access_token_expire_minutes: int, refresh_token_expire_days: int):
            self.secret_key = secret_key
            self.algorithm = algorithm
            self.access_token_expire_minutes = access_token_expire_minutes
            self.refresh_token_expire_days = refresh_token_expire_days


    def _encode(self, payload: dict) -> str:
            """Encode un payload en un token de rafraîchissement JWT."""
            return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)


    def _decode(self, token: str, expected_type: str) -> dict:
            """Décode un token de rafraîchissement JWT et vérifie sa validité."""
            try:
                required_claims = ["exp", "sub"]
                if expected_type == "refresh":
                    required_claims.append("jti")
                data = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], 
                                  options={"require": required_claims})
            except jwt.PyJWTError:
                raise InvalidToken()
    
            if data.get("type") != expected_type:
                raise InvalidToken()

            return data


    def create_access_token(self, actor: Actor) -> str:
        """Crée un token d'accès JWT pour l'acteur donné."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "sub": str(actor.id),
            "role": actor.role.value,
            "exp": expire.timestamp()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_access_token(self, user: User) -> str:
        """Crée un token d'accès JWT pour l'utilisateur donné."""
        now = datetime.now(timezone.utc)

        return self._encode({
    
            "sub": str(user.id),
            "role": user.role.value,
            "type": "access",
            "iat": now.timestamp(),
            "exp": (now + timedelta(minutes=self.access_token_expire_minutes)).timestamp()
        })

    def create_refresh_token(self, user: User) -> tuple[str, UUID, datetime]:
        """Crée un token de rafraîchissement JWT pour l'utilisateur donné."""
        now = datetime.now(timezone.utc)
        jti = uuid4()
        expires_at = now + timedelta(days=self.refresh_token_expire_days)

        payload = {
            "sub": str(user.id),
            "jti": str(jti),
            "type": "refresh",
            "iat": now.timestamp(),
            "exp": expires_at.timestamp()
        }
        token = self._encode(payload)
        return token, jti, expires_at


    def decode_access_token(self, token: str) -> Actor:
        """Décode un token d'accès JWT et retourne les informations de l'acteur."""
        data = self._decode(token, expected_type="access")
        try:
             return  Actor(id=UUID(data["sub"]), role=Role(data["role"]))
        except (ValueError, KeyError):
            raise InvalidToken()


    def decode_refresh_token(self, token: str) -> RefreshClaims:
        """Décode un token de rafraîchissement JWT et retourne les informations du jeton."""
        data = self._decode(token, expected_type="refresh")
        try:
            return RefreshClaims(
                user_id=UUID(data["sub"]),
                jti=UUID(data["jti"])
            )
        except (ValueError, KeyError):
            raise InvalidToken()
        

    



    
            
        
        