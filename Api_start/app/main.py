from fastapi import FastAPI

from app.api.nl2sql import router as nl2sql_router

app = FastAPI()

app.include_router(nl2sql_router)

@app.get("/health")
def health():
    return {"status": "ok"}


