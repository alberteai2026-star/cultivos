from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MarketOffer(Base):
    __tablename__ = 'market_offers'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey('market_listings.id'), nullable=False, index=True)
    buyer_name: Mapped[str] = mapped_column(String(150), nullable=False)
    buyer_contact: Mapped[str | None] = mapped_column(String(120), nullable=True)
    offered_price: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    requested_quantity: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default='nueva')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
