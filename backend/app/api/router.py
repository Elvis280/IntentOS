from fastapi import APIRouter
from app.api.vision import router as vision_router
from app.api.planner import router as planner_router
from app.api.executor import router as executor_router
from app.api.agent import router as agent_router
from app.api.verifier import router as verifier_router

router=APIRouter()
router.include_router(vision_router)
router.include_router(planner_router)
router.include_router(executor_router)
router.include_router(agent_router)
router.include_router(verifier_router)
