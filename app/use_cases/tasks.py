from uuid import UUID
from app.entities.entities import Actor, Task
from app.entities.exceptions import TaskNotFound, PermissionDenied
from app.use_cases.gateways import TaskRepository


UPDATE_FIELD = {"title", "description", "is_completed"}

def _get_authorized_task(
        task_repo: TaskRepository, actor: Actor, task_id: UUID
        ) -> Task:
    """Récupère une tâche par son ID et vérifie si l'acteur a le droit d'y accéder."""
    task = task_repo.get(task_id)
    if task is None:
        raise TaskNotFound()
    if not task.is_accessible_by(actor):
        raise PermissionDenied()
    return task


class CreateTask:
    """Use case pour créer une nouvelle tâche."""
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    def execute(self, actor: Actor, title: str, description: str | None = None) -> Task:
        """Crée une nouvelle tâche pour l'acteur donné."""
        task = Task(title=title, description=description, owner_id=actor.id)
        return self.task_repo.add(task)


class ListMyTasks:
    """Use case pour lister toutes les tâches d'un utilisateur."""
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    def execute(self, actor: Actor) -> list[Task]:
        """Retourne toutes les tâches appartenant à l'acteur donné."""
        return self.task_repo.list_by_owner(actor.id)


class ListAllTasks:
    """Use case pour lister toutes les tâches (réservé aux admins)."""
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    def execute(self, actor: Actor) -> list[Task]:
        """Retourne toutes les tâches si l'acteur est un admin."""
        if actor.role != "admin":
            raise PermissionDenied()
        return self.task_repo.list_all()


class GetTask:
    """Use case pour récupérer une tâche spécifique par son ID."""
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    def execute(self, actor: Actor, task_id: UUID) -> Task:
        """Récupère une tâche par son ID et vérifie l'accès de l'acteur."""
        return _get_authorized_task(self.task_repo, actor, task_id)


class UpdateTask:
    """Use case pour mettre à jour une tâche existante."""
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    def execute(self, actor: Actor, task_id: UUID, changes: dict) -> Task:
        """Met à jour les champs spécifiés d'une tâche si l'acteur a les droits."""
        task = _get_authorized_task(self.task_repo, actor, task_id)
        for key, value in changes.items():
            if key in UPDATE_FIELD:
                setattr(task, key, value)
        return self.task_repo.update(task)

class DeleteTask:
    """Use case pour supprimer une tâche existante."""
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    def execute(self, actor: Actor, task_id: UUID) -> None:
        """Supprime une tâche si l'acteur a les droits d'accès."""
        task = _get_authorized_task(self.task_repo, actor, task_id)
        self.task_repo.delete(task.id)