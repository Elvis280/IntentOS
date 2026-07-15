from fastapi import APIRouter
from pydantic import BaseModel

from app.services.planner import create_plan


router = APIRouter(
    prefix="/planner",
    tags=["Planner"]
)


class Goal(BaseModel):
    goal: str


@router.post("/plan")
async def generate_plan(data: Goal):

    plan = create_plan(data.goal)

    return plan