from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.marketplace_repository import MarketplaceRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class MarketplaceService:
    def __init__(self, db: Session):
        self.db = db
        self.market = MarketplaceRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_listings_for_user(self, user: User):
        return self.market.list_listings_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))

    def create_listing_for_user(self, *, user: User, farm_id: int, title: str, product_name: str, quantity: float, unit: str, unit_price: float, status_value: str, description: str | None, published_at: datetime):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        listing = self.market.create_listing(farm_id=farm_id, title=title, product_name=product_name, quantity=quantity, unit=unit, unit_price=unit_price, status=status_value, description=description, published_at=published_at)
        self.audit.add(module='marketplace', action='create_listing', user_id=user.id, farm_id=farm_id, record_id=str(listing.id))
        self.db.commit(); self.db.refresh(listing)
        return listing

    def list_offers_for_user(self, user: User):
        listings = self.market.list_listings_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))
        return self.market.list_offers_by_listing_ids([x.id for x in listings])

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
