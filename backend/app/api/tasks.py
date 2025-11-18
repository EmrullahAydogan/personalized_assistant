from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: int = 1,  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
):
    """Create a new task"""
    task = Task(
        user_id=user_id,
        **task_data.model_dump(),
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    return task


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    user_id: int = 1,  # TODO: Get from auth
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all tasks for a user"""
    query = select(Task).where(Task.user_id == user_id)

    if status_filter:
        query = query.where(Task.status == status_filter)

    query = query.order_by(Task.due_date.asc().nullslast())

    result = await db.execute(query)
    tasks = result.scalars().all()

    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    user_id: int = 1,  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
):
    """Get a specific task"""
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id,
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    user_id: int = 1,  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
):
    """Update a task"""
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id,
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Update fields
    update_data = task_data.model_dump(exclude_unset=True)

    # Handle status change to completed
    if "status" in update_data and update_data["status"] == TaskStatus.COMPLETED.value:
        update_data["completed_at"] = datetime.utcnow()

    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user_id: int = 1,  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
):
    """Delete a task"""
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id,
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    await db.delete(task)
    await db.commit()

    return None
