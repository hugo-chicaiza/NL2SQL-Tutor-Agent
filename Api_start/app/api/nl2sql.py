from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.db.database import AsyncSessionLocal
from app.services.nl2sql_service import NL2SQLService

router = APIRouter(prefix="/nl2sql", tags=["NL2SQL"])


# =========================================================
# REQUEST MODEL
# =========================================================

class NL2SQLRequest(BaseModel):
    question: str


# =========================================================
# RESPONSE MODEL
# =========================================================

class NL2SQLResponse(BaseModel):
    sql: str
    explanation: str
    rows: list
    execution_time: float
    llm_time: float


# =========================================================
# DB DEPENDENCY
# =========================================================

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# =========================================================
# ENDPOINT
# =========================================================

@router.post("/", response_model=NL2SQLResponse)
async def nl2sql_endpoint(
    payload: NL2SQLRequest,
    db=Depends(get_db)
):

    service = NL2SQLService(db)

    result = await service.run(payload.question)

    return NL2SQLResponse(
        sql=result.sql,
        explanation=result.explanation,
        rows=result.rows,
        execution_time=result.execution_time,
        llm_time=result.llm_time
    )