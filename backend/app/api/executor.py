from fastapi import APIRouter
from pydantic import BaseModel

from app.executor.executor import Executor

router = APIRouter(
    prefix="/executor",
    tags=["Executor"]
)

executor = Executor()


class Step(BaseModel):
    action: str
    target: str | None = None


@router.post("/execute")
async def execute(step: Step):

    executor.execute(step.model_dump())

    return {
        "status": "success"
    }