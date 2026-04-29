from pydantic import BaseModel, ConfigDict


class AdvertResponse(BaseModel):
    id: int
    auto_id: str
    title: str
    url: str
    phone_number: str

    model_config = ConfigDict(from_attributes=True)
