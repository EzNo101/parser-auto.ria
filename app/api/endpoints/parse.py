from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import StreamingResponse

from app.services.parse import ParseService
from app.core.dependencies import get_parse_service
from app.core.error import NoParsedAdverts, AdvertNotFoundError
from app.scraper.car_page import Advert as AdvertDict

router = APIRouter(prefix="/parse", tags=["parse"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=list[AdvertDict])
async def parse_adverts(
    url: str,
    max_pages: int = 1,
    parse_service: ParseService = Depends(get_parse_service),
):
    try:
        return await parse_service.parse(url, max_pages=max_pages)
    except NoParsedAdverts as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/get_vcf_file", status_code=status.HTTP_200_OK)
async def export_to_vcf(parse_service: ParseService = Depends(get_parse_service)):

    async def create_vcf():
        try:
            async for advert in await parse_service.stream_all():
                yield parse_service.build_vcard(
                    advert.title,
                    advert.phone_number,
                    advert.url,
                )
        except AdvertNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return StreamingResponse(
        create_vcf(),
        media_type="text/vcard",
        headers={"Content-Disposition": "attachment; filename=adverts.vcf"},
    )


@router.get("/get_csv_file", status_code=status.HTTP_200_OK)
async def export_to_csv(parse_service: ParseService = Depends(get_parse_service)):

    async def create_csv():
        yield "title,phone_number,url\n"
        try:
            async for advert in await parse_service.stream_all():
                yield parse_service.build_csv(
                    advert.title,
                    advert.phone_number,
                    advert.url,
                )
        except AdvertNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return StreamingResponse(
        create_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=adverts.csv"},
    )
