from fastapi import APIRouter
from app.api.vision import router as vision_router
from app.api.planner import router as planner_router

router=APIRouter()
router.include_router(vision_router)
router.include_router(planner_router)