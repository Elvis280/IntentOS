from fastapi import APIRouter
from app.api.vision import router as vision_router
from app.api.planner import router as planner_router
from app.api.executor import router as executor_router
from app.api.agent import router as agent_router
from app.api.verifier import router as verifier_router
from app.api.locator import router as locator_router
from app.api.reasoner import router as reasoner_router
from app.api.sessions import router as sessions_router
from app.api.settings import router as settings_router

router=APIRouter()
router.include_router(vision_router)
router.include_router(planner_router)
router.include_router(executor_router)
router.include_router(agent_router)
router.include_router(verifier_router)
router.include_router(locator_router)
router.include_router(reasoner_router)
router.include_router(sessions_router)
router.include_router(settings_router)