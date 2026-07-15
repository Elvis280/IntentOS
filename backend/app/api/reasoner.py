from fastapi import APIRouter
from pydantic import BaseModel

from app.services.reasoner import next_action
from app.vision.capture import ScreenCapture
from app.world.manager import world


router = APIRouter(
    prefix="/reasoner",
    tags=["Reasoner"]
)

capture = ScreenCapture()


class Goal(BaseModel):
    goal: str


@router.post("/next")
async def reason(data: Goal):

    image = capture.capture()

    current_world = world.get()

    if current_world is None:
        return {
            "error": "World model empty. Run /vision/analyze first."
        }

    result = next_action(
        data.goal,
        current_world.model_dump(),
        [],
        image
    )

    return result