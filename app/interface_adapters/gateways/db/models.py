from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String,Uuid
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship, Mapped

#1- Définition des modèles SQLAlchemy pour les entités du système : User, Task et RefreshToken.
class Base(DeclarativeBase):
    """Classe de base pour tous les modèles SQLAlchemy."""
    pass    


class UserModel(Base):
    """Modèle SQLAlchemy représentant un utilisateur."""
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=UUID)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    #tasks: Mapped[list["TaskModel"]] = relationship("TaskModel", back_populates="owner")


#2- Définition des modèles SQLAlchemy pour les entités du système : Task et RefreshToken.
class TaskModel(Base):
    """Modèle SQLAlchemy représentant une tâche."""
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=UUID)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

   # owner: Mapped["UserModel"] = relationship("UserModel", back_populates="tasks")


class RefreshTokenModel(Base):
    """Modèle SQLAlchemy représentant un jeton de rafraîchissement."""
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=UUID)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    #user: Mapped["UserModel"] = relationship("UserModel")