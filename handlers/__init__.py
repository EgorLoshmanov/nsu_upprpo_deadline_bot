from aiogram import Router

from .common import router as common_router
from .subjects import router as subjects_router
from .tasks import router as tasks_router
from .fallback import router as fallback_router

router = Router()
router.include_router(common_router)
router.include_router(subjects_router)
router.include_router(tasks_router)
# fallback подключаем последним, чтобы он ловил только то, что не обработали выше
router.include_router(fallback_router)
