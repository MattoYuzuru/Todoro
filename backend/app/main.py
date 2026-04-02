from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routes import todo_router, user_router

app = FastAPI(title="todoly", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(todo_router.router, tags=["To-Dos"])
app.include_router(user_router.router, tags=["Users"])


@app.get("/healthz")
def healthcheck():
    return {"status": "ok"}


@app.get("/")
def read_root():
    return {"message": "Welcome to Todoly."}
