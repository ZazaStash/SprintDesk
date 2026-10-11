from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select

from app.deps import CurrentUser, DB
from app.models import Task, User
from app.schemas import TaskCreate, TaskOut, TaskUpdate


router = APIRouter(prefix="/api/tasks", tags=["Задачи"])


def get_accessible_task(task_id: int, db: DB, user: User) -> Task:
    task = db.get(Task, task_id)
    if task is None or (user.role != "admin" and task.owner_id != user.id):
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


def validate_owner(owner_id: int, db: DB) -> None:
    if db.get(User, owner_id) is None:
        raise HTTPException(status_code=422, detail="Указанный участник не найден")


@router.get("", response_model=list[TaskOut])
def list_tasks(db: DB, user: CurrentUser):
    query = select(Task).order_by(Task.created_at.desc(), Task.id.desc())
    if user.role != "admin":
        query = query.where(Task.owner_id == user.id)
    return db.scalars(query).all()


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: DB, user: CurrentUser):
    owner_id = payload.owner_id if user.role == "admin" and payload.owner_id is not None else user.id
    if user.role != "admin" and payload.owner_id is not None and payload.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Назначать задачи другим может только администратор")
    validate_owner(owner_id, db)
    task = Task(**payload.model_dump(exclude={"owner_id"}), owner_id=owner_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: DB, user: CurrentUser):
    return get_accessible_task(task_id, db, user)


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: DB, user: CurrentUser):
    task = get_accessible_task(task_id, db, user)
    changes = payload.model_dump(exclude_unset=True)
    if any(value is None for value in changes.values()):
        raise HTTPException(status_code=422, detail="Поля не могут быть null")
    if "owner_id" in changes:
        if user.role != "admin" and changes["owner_id"] != user.id:
            raise HTTPException(status_code=403, detail="Назначать задачи другим может только администратор")
        validate_owner(changes["owner_id"], db)
    for key, value in changes.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: DB, user: CurrentUser):
    task = get_accessible_task(task_id, db, user)
    db.delete(task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
