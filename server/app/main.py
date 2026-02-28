from fastapi import FastAPI

app = FastAPI(title="kamishibai-server", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "api": "v0"}
