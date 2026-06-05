import os
from fastapi import FastAPI, Response

app = FastAPI()

VERSION = os.getenv("APP_VERSION", "v1")
FORCE_UNHEALTHY = os.getenv("FORCE_UNHEALTHY", "false").lower() == "true"


@app.get("/")
def root():
    return {"message": "Hello from dummy app", "version": VERSION}


@app.get("/health")
def health(response: Response):
    if FORCE_UNHEALTHY:
        response.status_code = 500
        return {"status": "unhealthy", "version": VERSION}
    return {"status": "ok", "version": VERSION}
