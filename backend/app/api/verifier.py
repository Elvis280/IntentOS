from fastapi import APIRouter
from pydantic import BaseModel

from app.services.verifier import verifier
from app.world.manager import world


router = APIRouter(
    prefix="/verifier",
    tags=["Verifier"]
)


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