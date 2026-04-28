from fastapi import APIRouter

from adverts import router as adverts_router

router = APIRouter()
router.include_router(adverts_router)
