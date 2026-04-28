from fastapi import APIRouter, status, HTTPException

from app.services.parse import ParseService
from app.core.dependencies import get_parse_service
from app.core.error import NoParsedAdverts
from app.scraper.car_page import Advert as AdvertDict

router = APIRouter(prefix="/parse", tags=["parse"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=list[AdvertDict])
async def parse_adverts(
    url: str, max_pages: int = 1, parse_service: ParseService = get_parse_service()
):
    try:
        return await parse_service.parse(url, max_pages=max_pages)
    except NoParsedAdverts as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
