from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Advert(Base):
    __tablename__ = "parsed_adverts"

    id: Mapped[int] = mapped_column(primary_key=True)
    auto_id: Mapped[int] = mapped_column(unique=True, index=True)
    url: Mapped[str] = mapped_column(String(1024), unique=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    phone_number: Mapped[str] = mapped_column(String(20), index=True)
