"""
FlyRank W1 · A3 — Task API on containerized Postgres.
Same five CRUD doors as A1/A2; storage is now a real Postgres server.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

import repository as repo


@asynccontextmanager
async def lifespan(_: FastAPI):
    repo.init_db()
    yield


app = FastAPI(
    title="Task API",
    version="3.0.0",
    description=(
        "FlyRank W1 · A3 — the task CRUD API running against **PostgreSQL** in Docker. "
        "Start everything with `docker compose up`. Same endpoints as A1/A2."
    ),
    lifespan=lifespan,
)


class TaskOut(BaseModel):
    id: int
    title: str
    done: bool


class ErrorOut(BaseModel):
    error: str


@app.get("/", tags=["meta"])
def root():
    return {
        "name": "Task API",
        "version": "3.0",
        "storage": "postgres",
        "endpoints": ["/tasks"],
    }


@app.get("/health", tags=["meta"], summary="Liveness + DB ping")
def health():
    try:
        db_ok = repo.ping()
    except Exception:
        db_ok = False
    return {"status": "ok", "db": "ok" if db_ok else "down"}


@app.get("/tasks", response_model=list[TaskOut], tags=["tasks"])
def list_tasks():
    return repo.list_tasks()


@app.get("/tasks/{task_id}", response_model=TaskOut, tags=["tasks"],
         responses={404: {"model": ErrorOut}})
def get_task(task_id: int):
    task = repo.get_task(task_id)
    if task is None:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    return task


@app.post("/tasks", response_model=TaskOut, status_code=201, tags=["tasks"],
          responses={400: {"model": ErrorOut}})
async def create_task(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Request body must be JSON"})
    if not isinstance(body, dict):
        return JSONResponse(status_code=400, content={"error": "Request body must be a JSON object"})
    title = body.get("title")
    if title is None or not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "title is required and must be a non-empty string"},
        )
    return repo.create_task(title.strip())


@app.put("/tasks/{task_id}", response_model=TaskOut, tags=["tasks"],
         responses={400: {"model": ErrorOut}, 404: {"model": ErrorOut}})
async def update_task(task_id: int, request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Request body must be JSON"})
    if not isinstance(body, dict) or ("title" not in body and "done" not in body):
        return JSONResponse(
            status_code=400,
            content={"error": "Request body must include title and/or done"},
        )

    current = repo.get_task(task_id)
    if current is None:
        return JSONResponse(status_code=404, content={"error": "Task not found"})

    title = current["title"]
    done = current["done"]
    if "title" in body:
        if not isinstance(body["title"], str) or not body["title"].strip():
            return JSONResponse(status_code=400, content={"error": "title must be a non-empty string"})
        title = body["title"].strip()
    if "done" in body:
        if not isinstance(body["done"], bool):
            return JSONResponse(status_code=400, content={"error": "done must be a boolean"})
        done = body["done"]

    return repo.update_task(task_id, title, done)


@app.delete("/tasks/{task_id}", status_code=204, tags=["tasks"], response_class=Response)
def delete_task(task_id: int):
    if not repo.delete_task(task_id):
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    return Response(status_code=204)
