from fastapi import FastAPI
import uvicorn

from .assets import router as assets_router
from .projects import router as projects_router
from .saves import router as saves_router
from .scenario import router as scenario_router

app = FastAPI(title="kamishibai-server", version="0.1.0")
app.include_router(projects_router)
app.include_router(scenario_router)
app.include_router(saves_router)
app.include_router(assets_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "api": "v0"}


def run() -> None:
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
