from fastapi import APIRouter

from app.api.endpoints.adverts import router as adverts_router
from app.api.endpoints.parse import router as parse_router

router = APIRouter()
router.include_router(adverts_router)
router.include_router(parse_router)
