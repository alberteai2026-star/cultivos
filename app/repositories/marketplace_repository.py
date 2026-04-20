from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.market_listing import MarketListing
from app.models.market_offer import MarketOffer


class MarketplaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_listing(self, *, farm_id: int, title: str, product_name: str, quantity: float, unit: str, unit_price: float, status: str, description: str | None, published_at: datetime) -> MarketListing:
        listing = MarketListing(
            farm_id=farm_id,
            title=title,
            product_name=product_name,
            quantity=quantity,
            unit=unit,
            unit_price=unit_price,
            status=status,
            description=description,
            published_at=published_at,
        )
        self.db.add(listing)
        self.db.flush()
        return listing

    def list_listings_by_farm_ids(self, farm_ids: list[int]) -> list[MarketListing]:
        if not farm_ids:
            return []
        q = select(MarketListing).where(MarketListing.farm_id.in_(farm_ids)).order_by(MarketListing.id.desc())
        return list(self.db.scalars(q).all())

    def get_listing(self, listing_id: int) -> MarketListing | None:
        return self.db.get(MarketListing, listing_id)

    def create_offer(self, *, listing_id: int, buyer_name: str, buyer_contact: str | None, offered_price: float, requested_quantity: float, message: str | None, status: str) -> MarketOffer:
        offer = MarketOffer(
            listing_id=listing_id,
            buyer_name=buyer_name,
            buyer_contact=buyer_contact,
            offered_price=offered_price,
            requested_quantity=requested_quantity,
            message=message,
            status=status,
        )
        self.db.add(offer)
        self.db.flush()
        return offer

    def list_offers_by_listing_ids(self, listing_ids: list[int]) -> list[MarketOffer]:
        if not listing_ids:
            return []
        q = select(MarketOffer).where(MarketOffer.listing_id.in_(listing_ids)).order_by(MarketOffer.id.desc())
        return list(self.db.scalars(q).all())
