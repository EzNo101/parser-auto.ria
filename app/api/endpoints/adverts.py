from fastapi import APIRouter, HTTPException, status

from app.services.parse import ParseService
from app.core.error import AdvertNotFoundError
from app.core.dependencies import get_parse_service
from app.models.advert import Advert


router = APIRouter(prefix="/adverts", tags=["adverts"])


@router.get("/all", status_code=status.HTTP_200_OK, response_model=list[Advert])
async def get_all_advert(parse_service: ParseService = get_parse_service()):
    try:
        return await parse_service.get_all()
    except AdvertNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/id/{advert_id}", status_code=status.HTTP_200_OK, response_model=Advert)
async def get_advert_by_id(
    advert_id: int, parse_service: ParseService = get_parse_service()
):
    try:
        return await parse_service.get_by_id(advert_id)
    except AdvertNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/auto_id/{auto_id}", status_code=status.HTTP_200_OK, response_model=Advert)
async def get_advert_by_auto_id(
    auto_id: str, parse_service: ParseService = get_parse_service()
):
    try:
        return await parse_service.get_by_auto_id(auto_id)
    except AdvertNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/phone/{phone_number}", status_code=status.HTTP_200_OK, response_model=Advert
)
async def get_advert_by_phone_number(
    phone_number: str, parse_service: ParseService = get_parse_service()
):
    try:
        return await parse_service.get_by_number(phone_number)
    except AdvertNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
