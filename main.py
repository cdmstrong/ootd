from __future__ import annotations

import uuid

from fastapi import BackgroundTasks, FastAPI, HTTPException

from app.models import CreateOutfitTaskRequest, TaskStatusResponse
from app.prompts import build_prompt
from app.generator import generate_outfit_image
from app.store import InMemoryTaskStore, TaskManager


app = FastAPI(title="OOTD Outfit Generator", version="0.1.0")

store = InMemoryTaskStore()
manager = TaskManager(store)


async def _process_task(task_id: str, req: CreateOutfitTaskRequest) -> None:
    try:
        await manager.set_running(task_id)
        prompt = build_prompt(req)
        out_path = generate_outfit_image(task_id=task_id, prompt=prompt, req=req)
        await manager.set_succeeded(
            task_id,
            result={
                "image_path": out_path,
                "prompt": prompt,
            },
        )
    except Exception as exc:  # noqa: BLE001
        await manager.set_failed(task_id, error_message=str(exc))


@app.post("/api/v1/outfit/tasks", response_model=TaskStatusResponse)
async def create_outfit_task(
    request: CreateOutfitTaskRequest,
    background_tasks: BackgroundTasks,
) -> TaskStatusResponse:
    # Pydantic validators already ensured image count constraints
    try:
        # Force validation manually to surface root_validator errors early
        request = CreateOutfitTaskRequest(**request.dict())
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(e)) from e

    task_id = uuid.uuid4().hex
    await manager.create_task(task_id, request)
    background_tasks.add_task(_process_task, task_id, request)
    return TaskStatusResponse(task_id=task_id, status="PENDING", result=None, error_message=None)


@app.get("/api/v1/outfit/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_outfit_task(task_id: str) -> TaskStatusResponse:
    task = await manager.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatusResponse(
        task_id=task.task_id,
        status=task.status,
        result=task.result,
        error_message=task.error_message,
    )


__all__ = ["app"]


