from datetime import datetime

from sqlalchemy import func, select
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

    def list_listings_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        status_value: str | None = None,
        product_search: str | None = None,
        published_from: datetime | None = None,
        published_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[MarketListing]]:
        if not farm_ids:
            return 0, []

        q = select(MarketListing).where(MarketListing.farm_id.in_(farm_ids))
        count_q = select(func.count(MarketListing.id)).where(MarketListing.farm_id.in_(farm_ids))

        if farm_id is not None:
            q = q.where(MarketListing.farm_id == farm_id)
            count_q = count_q.where(MarketListing.farm_id == farm_id)
        if status_value is not None:
            q = q.where(MarketListing.status == status_value)
            count_q = count_q.where(MarketListing.status == status_value)
        if product_search is not None:
            pattern = f'%{product_search}%'
            q = q.where(MarketListing.product_name.ilike(pattern))
            count_q = count_q.where(MarketListing.product_name.ilike(pattern))
        if published_from is not None:
            q = q.where(MarketListing.published_at >= published_from)
            count_q = count_q.where(MarketListing.published_at >= published_from)
        if published_to is not None:
            q = q.where(MarketListing.published_at <= published_to)
            count_q = count_q.where(MarketListing.published_at <= published_to)

        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(MarketListing.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_listing(self, listing_id: int) -> MarketListing | None:
        return self.db.get(MarketListing, listing_id)

    def update_listing_fields(
        self,
        listing: MarketListing,
        *,
        title: str | None,
        product_name: str | None,
        quantity: float | None,
        unit: str | None,
        unit_price: float | None,
        description: str | None,
    ) -> MarketListing:
        if title is not None:
            listing.title = title
        if product_name is not None:
            listing.product_name = product_name
        if quantity is not None:
            listing.quantity = quantity
        if unit is not None:
            listing.unit = unit
        if unit_price is not None:
            listing.unit_price = unit_price
        if description is not None:
            listing.description = description
        self.db.flush()
        return listing

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

    def list_offers_by_listing_ids(
        self,
        listing_ids: list[int],
        *,
        listing_id: int | None = None,
        status_value: str | None = None,
        buyer_search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[MarketOffer]]:
        if not listing_ids:
            return 0, []

        q = select(MarketOffer).where(MarketOffer.listing_id.in_(listing_ids))
        count_q = select(func.count(MarketOffer.id)).where(MarketOffer.listing_id.in_(listing_ids))

        if listing_id is not None:
            q = q.where(MarketOffer.listing_id == listing_id)
            count_q = count_q.where(MarketOffer.listing_id == listing_id)
        if status_value is not None:
            q = q.where(MarketOffer.status == status_value)
            count_q = count_q.where(MarketOffer.status == status_value)
        if buyer_search is not None:
            pattern = f'%{buyer_search}%'
            q = q.where(MarketOffer.buyer_name.ilike(pattern))
            count_q = count_q.where(MarketOffer.buyer_name.ilike(pattern))

        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(MarketOffer.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_offer(self, offer_id: int) -> MarketOffer | None:
        return self.db.get(MarketOffer, offer_id)
