from fastapi import FastAPI
import uvicorn

app = FastAPI(title="kamishibai-server", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "api": "v0"}


def run() -> None:
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
