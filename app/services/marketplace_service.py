from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.marketplace_repository import MarketplaceRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.marketplace import MarketListingListResponse, MarketOfferListResponse


class MarketplaceService:
    def __init__(self, db: Session):
        self.db = db
        self.market = MarketplaceRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_listings_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        status_value: str | None = None,
        product_search: str | None = None,
        published_from: datetime | None = None,
        published_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> MarketListingListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.market.list_listings_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            status_value=status_value,
            product_search=product_search,
            published_from=published_from,
            published_to=published_to,
            limit=limit,
            offset=offset,
        )
        return MarketListingListResponse(total=total, items=items)

    def create_listing_for_user(self, *, user: User, farm_id: int, title: str, product_name: str, quantity: float, unit: str, unit_price: float, status_value: str, description: str | None, published_at: datetime):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        listing = self.market.create_listing(farm_id=farm_id, title=title, product_name=product_name, quantity=quantity, unit=unit, unit_price=unit_price, status=status_value, description=description, published_at=published_at)
        self.audit.add(module='marketplace', action='create_listing', user_id=user.id, farm_id=farm_id, record_id=str(listing.id))
        self.db.commit(); self.db.refresh(listing)
        return listing

    def get_listing_for_user(self, *, user: User, listing_id: int):
        listing = self.market.get_listing(listing_id)
        if listing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Publicación no encontrada')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=listing.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta publicación')
        return listing

    def update_listing_for_user(
        self,
        *,
        user: User,
        listing_id: int,
        title: str | None,
        product_name: str | None,
        quantity: float | None,
        unit: str | None,
        unit_price: float | None,
        description: str | None,
    ):
        listing = self.get_listing_for_user(user=user, listing_id=listing_id)
        updated = self.market.update_listing_fields(
            listing,
            title=title,
            product_name=product_name,
            quantity=quantity,
            unit=unit,
            unit_price=unit_price,
            description=description,
        )
        self.audit.add(module='marketplace', action='update_listing', user_id=user.id, farm_id=listing.farm_id, record_id=str(listing.id))
        self.db.commit(); self.db.refresh(updated)
        return updated

    def list_offers_for_user(
        self,
        user: User,
        *,
        listing_id: int | None = None,
        status_value: str | None = None,
        buyer_search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> MarketOfferListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        total_listings, listings = self.market.list_listings_by_farm_ids(farm_ids, limit=100000, offset=0)
        listing_ids = [x.id for x in listings]
        if listing_id is not None and listing_id not in listing_ids:
            if total_listings == 0:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso al listado de ofertas')
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta publicación')
        total, items = self.market.list_offers_by_listing_ids(
            listing_ids,
            listing_id=listing_id,
            status_value=status_value,
            buyer_search=buyer_search,
            limit=limit,
            offset=offset,
        )
        return MarketOfferListResponse(total=total, items=items)

    def create_offer_for_user(self, *, user: User, listing_id: int, buyer_name: str, buyer_contact: str | None, offered_price: float, requested_quantity: float, message: str | None, status_value: str):
        listing = self.market.get_listing(listing_id)
        if listing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Publicación no encontrada')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=listing.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta publicación')
        offer = self.market.create_offer(listing_id=listing_id, buyer_name=buyer_name, buyer_contact=buyer_contact, offered_price=offered_price, requested_quantity=requested_quantity, message=message, status=status_value)
        self.audit.add(module='marketplace', action='create_offer', user_id=user.id, farm_id=listing.farm_id, record_id=str(offer.id))
        self.db.commit(); self.db.refresh(offer)
        return offer

    def update_offer_status_for_user(self, *, user: User, offer_id: int, status_value: str):
        offer = self.market.get_offer(offer_id)
        if offer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Oferta no encontrada')
        listing = self.market.get_listing(offer.listing_id)
        if listing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Publicación no encontrada')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=listing.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta oferta')
        offer.status = status_value
        self.audit.add(module='marketplace', action='update_offer_status', user_id=user.id, farm_id=listing.farm_id, record_id=str(offer.id))
        self.db.commit(); self.db.refresh(offer)
        return offer
