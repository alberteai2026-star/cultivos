from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.marketplace import MarketListingCreateRequest, MarketListingOut, MarketOfferCreateRequest, MarketOfferOut
from app.services.marketplace_service import MarketplaceService

router = APIRouter()


@router.get('/listings', response_model=list[MarketListingOut])
def list_market_listings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MarketplaceService(db).list_listings_for_user(user)


@router.post('/listings', response_model=MarketListingOut, status_code=201)
def create_market_listing(payload: MarketListingCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MarketplaceService(db).create_listing_for_user(user=user, farm_id=payload.farm_id, title=payload.title, product_name=payload.product_name, quantity=payload.quantity, unit=payload.unit, unit_price=payload.unit_price, status_value=payload.status, description=payload.description, published_at=payload.published_at)


@router.get('/offers', response_model=list[MarketOfferOut])
def list_market_offers(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MarketplaceService(db).list_offers_for_user(user)


@router.post('/offers', response_model=MarketOfferOut, status_code=201)
def create_market_offer(payload: MarketOfferCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MarketplaceService(db).create_offer_for_user(user=user, listing_id=payload.listing_id, buyer_name=payload.buyer_name, buyer_contact=payload.buyer_contact, offered_price=payload.offered_price, requested_quantity=payload.requested_quantity, message=payload.message, status_value=payload.status)
