from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Dict, Optional

from .models import CreateOutfitTaskRequest, TaskInfo, TaskStatus


class InMemoryTaskStore:
    """
    Simple in-memory task store.

    This is suitable for local development and can later be replaced
    by a Redis-backed implementation with the same interface.
    """

    def __init__(self) -> None:
        self._tasks: Dict[str, TaskInfo] = {}
        # Protect concurrent access in async context
        self._lock = asyncio.Lock()

    async def get_task(self, task_id: str) -> Optional[TaskInfo]:
        async with self._lock:
            return self._tasks.get(task_id)

    async def upsert_task(self, task: TaskInfo) -> None:
        async with self._lock:
            self._tasks[task.task_id] = task

    async def update_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: Optional[Dict] = None,
        error_message: Optional[str] = None,
    ) -> None:
        async with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return
            task.status = status
            task.updated_at = datetime.utcnow()
            if result is not None:
                task.result = result
            if error_message is not None:
                task.error_message = error_message
            self._tasks[task_id] = task


class TaskManager:
    """
    High-level task manager that orchestrates creation and updates.
    """

    def __init__(self, store: InMemoryTaskStore) -> None:
        self._store = store

    async def create_task(self, task_id: str, req: CreateOutfitTaskRequest) -> TaskInfo:
        now = datetime.utcnow()
        task = TaskInfo(
            task_id=task_id,
            status="PENDING",
            created_at=now,
            updated_at=now,
            input=req,
            result=None,
            error_message=None,
        )
        await self._store.upsert_task(task)
        return task

    async def set_running(self, task_id: str) -> None:
        await self._store.update_status(task_id, status="RUNNING")

    async def set_succeeded(self, task_id: str, result: Dict) -> None:
        await self._store.update_status(task_id, status="SUCCEEDED", result=result)

    async def set_failed(self, task_id: str, error_message: str) -> None:
        await self._store.update_status(task_id, status="FAILED", error_message=error_message)

    async def get_task(self, task_id: str) -> Optional[TaskInfo]:
        return await self._store.get_task(task_id)


