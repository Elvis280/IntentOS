from fastapi import APIRouter
from app.vision.capture import ScreenCapture
from app.vision.llm import analyze
from app.world.manager import world
from app.vision.analyzer import build_world
import base64 
import io

router =APIRouter(prefix="/vision",
                  tags=["Vision"])

capture=ScreenCapture()

@router.post("/analyze")
async def analyze_screen():

    image = capture.capture()

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    encoded = base64.b64encode(buffer.getvalue()).decode()

    vision = analyze(image)

    state = build_world(vision)

    world.update(state)

    return {
        "image": encoded,
        "world": world.get()
    }

@router.post("/observe")
async def observe_screen():

    image = capture.capture()

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    encoded = base64.b64encode(buffer.getvalue()).decode()

    return {
        "image": encoded
    }