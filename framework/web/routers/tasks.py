from uuid import UUID
from fastapi import APIRouter, Depends

from app.entities.entities import Actor, Role
from  framework.web.dependencies import get_create_task, get_delete_task, get_list_my_tasks, get_list_all_tasks, get_get_task, get_update_task, get_current_actor, require_role
from app.interface_adapters.schemas import TaskCreate, TaskResponse, TaskUpdate


router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(body: TaskCreate,
                actor: Actor = Depends(get_current_actor),
                use_case = Depends(get_create_task)):
    """Crée une nouvelle tâche."""
    return use_case.execute(actor, body.title, body.description)
  

@router.get("/", response_model=list[TaskResponse])
def list_my_tasks(actor: Actor = Depends(get_current_actor),
                  use_case = Depends(get_list_my_tasks)):
    """Liste les tâches de l'utilisateur actuel."""
    return use_case.execute(actor)


# IMPORTANT : declarer cette route avant '/tasks/{task_id}' pour éviter les conflits de routage
@router.get("admin/all", response_model=list[TaskResponse],
             dependencies=[Depends(require_role(Role.ADMIN))])
def list_all_tasks(use_case = Depends(get_list_all_tasks)):
    """Liste toutes les tâches."""
    return use_case.execute()



@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: UUID,
             actor: Actor = Depends(get_current_actor),
             use_case = Depends(get_get_task)):
    """Récupère une tâche spécifique par son ID."""
    return use_case.execute(actor, task_id)

@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: UUID,
                body: TaskUpdate,
                actor: Actor = Depends(get_current_actor),
                use_case = Depends(get_update_task)):
    """Met à jour une tâche spécifique par son ID."""
    return use_case.execute(actor, task_id, body.title, body.description, body.is_completed)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: UUID,
                actor: Actor = Depends(get_current_actor),
                use_case = Depends(get_delete_task)):
    """Supprime une tâche spécifique par son ID."""
    use_case.execute(actor, task_id)
    return None