from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from  app.use_cases.gateways import TaskRepository, RefreshTokenRepository, UserRepository
from  app.interface_adapters.gateways.db.models import TaskModel, RefreshTokenModel, UserModel
from  app.entities.entities import Task, RefreshToken, User, Role


# Implémentation des repositories utilisant SQLAlchemy pour interagir avec la base de données.


#1- Implémentation du UserRepository utilisant SQLAlchemy.
class SqlAlchemyUserRepository(UserRepository):
    """Implémentation du UserRepository utilisant SQLAlchemy."""
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _to_entity(user_model: UserModel) -> User:
        """Convertit un modèle SQLAlchemy UserModel en entité User."""
        return User(
            id=user_model.id,
            email=user_model.email,
            hashed_password=user_model.hashed_password,
            role=Role(user_model.role),
            is_active=user_model.is_active
        )

    def get_by_id(self, user_id: UUID) -> User | None:
        """Récupère un utilisateur par son ID."""
        user_model = self.session.get(UserModel, user_id)
        return self._to_entity(user_model) if user_model else None

    def get_by_email(self, email: str) -> User | None:
        """Récupère un utilisateur par son email."""
        m = self.session.scalar(select(UserModel).where(UserModel.email == email))
        return self._to_entity(m) if m else None

    def add(self, user: User) -> User:
        """Ajoute un nouvel utilisateur à la base de données."""
        user_model = UserModel(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role.value,
            is_active=user.is_active
        )
        self.session.add(user_model)
        self.session.commit()
        return self._to_entity(user_model)
    

#2- Implémentation du TaskRepository utilisant SQLAlchemy.
class SqlAlchemyTaskRepository(TaskRepository):
    """Implémentation du TaskRepository utilisant SQLAlchemy."""
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _to_entity(task_model: TaskModel) -> Task:
        """Convertit un modèle SQLAlchemy TaskModel en entité Task."""
        return Task(
            id=task_model.id,
            title=task_model.title,
            description=task_model.description,
            is_completed=task_model.is_completed,
            owner_id=task_model.owner_id,
            created_at=task_model.created_at
        )

     # methodes  ajouter pour le repository TaskRepository
    def add(self, task: Task) -> Task:
        """Ajoute une nouvelle tâche à la base de données."""
        task_model = TaskModel(
            id=task.id,
            title=task.title,
            description=task.description,
            is_completed=task.is_completed,
            owner_id=task.owner_id,
            created_at=task.created_at
        )
        self.session.add(task_model)
        self.session.commit()
        return self._to_entity(task_model)
    
    # methode recupérer une tâche par son ID
    def get(self, task_id: UUID) -> Task | None:
            """Récupère une tâche par son ID."""
            task_model = self.session.get(TaskModel, task_id)
            return self._to_entity(task_model) if task_model else None

    # methode lister toutes les tâches appartenant à un utilisateur spécifique
    def list_by_owner(self, owner_id: UUID) -> list[Task]:
        """Liste toutes les tâches appartenant à un utilisateur spécifique."""
        rows = self.session.scalars(
            select(TaskModel)
            .where(TaskModel.owner_id == owner_id)
            .order_by(TaskModel.created_at.desc())
        )
        return [self._to_entity(m) for m in rows]
    

     #methode lister toutes les tâches dans la base de données
    def list_all(self) -> list[Task]:
        """Liste toutes les tâches dans la base de données."""
        task_models =  self.session.scalars(
            select(TaskModel)
            .order_by(TaskModel.created_at.desc()))
        return [self._to_entity(m) for m in task_models]

    #methode mettre à jour une tâche existante dans la base de données
    def update(self, task: Task) -> Task:
        """Met à jour une tâche existante dans la base de données."""
        self.session.execute(
            update(TaskModel)
            .where(TaskModel.id == task.id)
            .values(
                title=task.title,
                description=task.description,
                is_completed=task.is_completed
            )
        )
        self.session.commit()
        return task

    #methode supprimer une tâche de la base de données
    def delete(self, task_id: UUID) -> None:
        """Supprime une tâche de la base de données."""
        m = self.session.get(TaskModel, task_id)
        if m:
            self.session.delete(m)
            self.session.commit()


#3- Implémentation du RefreshTokenRepository utilisant SQLAlchemy.
class SqlAlchemyRefreshTokenRepository(RefreshTokenRepository):
    """Implémentation du RefreshTokenRepository utilisant SQLAlchemy."""
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _to_entity(token_model: RefreshTokenModel) -> RefreshToken:
        """Convertit un modèle SQLAlchemy RefreshTokenModel en entité RefreshToken."""
        return RefreshToken(
            id=token_model.id,
            user_id=token_model.user_id,
            expires_at=token_model.expires_at,
            revoked=token_model.revoked,
        )

    def get(self, token_id: UUID) -> RefreshToken | None:
        """Récupère un jeton de rafraîchissement par son ID."""
        token_model = self.session.get(RefreshTokenModel, token_id)
        return self._to_entity(token_model) if token_model else None

    def add(self, token: RefreshToken) -> RefreshToken:
        """Ajoute un nouveau jeton de rafraîchissement à la base de données."""
        token_model = RefreshTokenModel(
            id=token.id,
            user_id=token.user_id,
            expires_at=token.expires_at,
            revoked=token.revoked,
        )
        self.session.add(token_model)
        self.session.commit()
        return self._to_entity(token_model)

    def revoke(self, token_id: UUID) -> None:
        """Révoque un jeton de rafraîchissement en le marquant comme révoqué."""
        self.session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.id == token_id)
            .values(revoked=True)
        )
        self.session.commit()

    def revoke_all_for_user(self, user_id: UUID) -> None:
        """Révoque tous les jetons de rafraîchissement d'un utilisateur."""
        self.session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .values(revoked=True)
        )
        self.session.commit()