from fastapi import APIRouter
from pydantic import BaseModel

from app.vision.capture import ScreenCapture
from app.experimental.locator import locate


router = APIRouter(
    prefix="/locator",
    tags=["Locator"]
)

capture = ScreenCapture()


class Target(BaseModel):
    target: str


@router.post("/find")
async def find(data: Target):

    image = capture.capture()

    result = locate(
        image,
        data.target
    )

    return result