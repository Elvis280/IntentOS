from fastapi import APIRouter
from pydantic import BaseModel

from app.verifier.verifier import Verifier
from app.world.manager import world

router = APIRouter(
    prefix="/verifier",
    tags=["Verifier"]
)

verifier = Verifier()


class VerifyRequest(BaseModel):
    step: dict


@router.post("/verify")
async def verify(data: VerifyRequest):

    result = verifier.verify(
        world.get(),
        data.step
    )

    return {
        "verified": result
    }