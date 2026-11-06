from collections.abc import Iterator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as _Session, sessionmaker as _sessionmaker

from framework.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
Session = _sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session() -> Iterator[_Session]:
    """Fournit une session SQLAlchemy pour interagir avec la base de données."""
    session = Session()
    try:
        yield session
    finally:
        session.close()