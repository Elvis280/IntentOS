from fastapi import APIRouter
from pydantic import BaseModel
from app.verifier.verifier import verifier
from app.world.manager import world
from app.vision.capture import ScreenCapture
from app.vision.llm import analyze
from app.vision.analyzer import build_world
from app.planner.planner import create_plan
from app.executor.executor import Executor

capture = ScreenCapture()



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

            image = capture.capture()
            vision = analyze(image)
            state = build_world(vision)
            world.update(state)

            verified = verifier.verify(
                world.get(),
                step
            )

            results.append({
                "step": step,
                "status": "success" if verified else "failed",
                "verified": verified
            })

            if not verified:
                break

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