from fastapi import APIRouter

from app import assets, projects, saves, scenario

router = APIRouter(prefix="/api/v0")
router.include_router(projects.router)
router.include_router(scenario.router)
router.include_router(saves.router)
router.include_router(assets.router)
