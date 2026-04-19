from aiogram import Router

from .common import router as common_router
from .subjects import router as subjects_router

router = Router()
router.include_router(common_router)
router.include_router(subjects_router)
