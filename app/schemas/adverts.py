from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AdvertResponse(BaseModel):
    id: int
    auto_id: str
    title: str
    url: str
    phone_number: str

    model_config = ConfigDict(from_attributes=True)


class JobAdvertResponse(BaseModel):
    id: int
    url: str
    max_pages: int
    interval_hours: int
    active: bool
    last_run_at: datetime | None
    next_run_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class JobAdvertUpdate(BaseModel):
    url: str | None = Field(default=None, max_length=1024)
    max_pages: int | None = Field(default=None, ge=1)
    interval_hours: int | None = Field(default=None, ge=1)
    active: bool | None

    model_config = ConfigDict(extra="forbid")


class JobAdvertCreate(BaseModel):
    url: str = Field(max_length=1024)
    max_pages: int = Field(default=1, ge=1)
    interval_hours: int = Field(default=1, ge=1)
    active: bool = Field(default=True)

    model_config = ConfigDict(extra="forbid")
