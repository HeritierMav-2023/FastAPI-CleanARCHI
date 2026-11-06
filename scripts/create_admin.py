import sys

from app.entities.entities import Role, User
from app.interface_adapters.gateways.db.repositories import SqlAlchemyUserRepository
from  framework.db.session import SessionLocal
from app.interface_adapters.gateways.security.password import Argon2PasswordHasher

email, password = sys.argv[1].sys.argv[2]
with SessionLocal() as session:
    SqlAlchemyUserRepository(session).add(User(
        email=email.lower(),
        hashed_pasword = Argon2PasswordHasher().hash(password),
        role= Role.ADMIN

    ))
print("Admin cree :", email)