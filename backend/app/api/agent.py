from fastapi import APIRouter
from pydantic import BaseModel

from app.planner.planner import create_plan
from app.executor.executor import Executor

router = APIRouter(
    prefix="/agent",
    tags=["Agent"]
)

executor = Executor()

class Goal(BaseModel):
    goal: str
    max_steps: int = 1


@router.post("/run")
async def run_agent(data: Goal):

    plan = create_plan(data.goal)

    results = []

    for step in plan["steps"][:data.max_steps]:

        try:

            executor.execute(step)

            results.append({
                "step": step,
                "status": "success"
            })

        except Exception as e:

            results.append({
                "step": step,
                "status": "failed",
                "error": str(e)
            })

            break

    return {
        "goal": plan["goal"],
        "plan": plan["steps"],
        "results": results
    }