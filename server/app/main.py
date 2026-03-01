from fastapi import FastAPI
import uvicorn

from app.api_v0 import router as api_v0_router

app = FastAPI(title="kamishibai-server", version="0.1.0")
app.include_router(api_v0_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "api": "v0"}


def run() -> None:
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
