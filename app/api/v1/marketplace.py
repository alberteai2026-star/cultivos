from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.marketplace import (
    MarketListingCreateRequest,
    MarketListingListResponse,
    MarketListingOut,
    MarketListingUpdateRequest,
    MarketOfferCreateRequest,
    MarketOfferListResponse,
    MarketOfferOut,
    MarketOfferStatusUpdateRequest,
)
from app.services.marketplace_service import MarketplaceService

router = APIRouter()


@router.get('/listings', response_model=MarketListingListResponse)
def list_market_listings(
    farm_id: int | None = Query(default=None, ge=1),
    status_value: str | None = Query(default=None, alias='status'),
    product_search: str | None = Query(default=None),
    published_from: datetime | None = Query(default=None),
    published_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return MarketplaceService(db).list_listings_for_user(
        user,
        farm_id=farm_id,
        status_value=status_value,
        product_search=product_search,
        published_from=published_from,
        published_to=published_to,
        limit=limit,
        offset=offset,
    )


@router.post('/listings', response_model=MarketListingOut, status_code=201)
def create_market_listing(payload: MarketListingCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MarketplaceService(db).create_listing_for_user(user=user, farm_id=payload.farm_id, title=payload.title, product_name=payload.product_name, quantity=payload.quantity, unit=payload.unit, unit_price=payload.unit_price, status_value=payload.status, description=payload.description, published_at=payload.published_at)


@router.get('/listings/{listing_id}', response_model=MarketListingOut)
def get_market_listing(listing_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MarketplaceService(db).get_listing_for_user(user=user, listing_id=listing_id)


@router.patch('/listings/{listing_id}', response_model=MarketListingOut)
def update_market_listing(listing_id: int, payload: MarketListingUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MarketplaceService(db).update_listing_for_user(
        user=user,
        listing_id=listing_id,
        title=payload.title,
        product_name=payload.product_name,
        quantity=payload.quantity,
        unit=payload.unit,
        unit_price=payload.unit_price,
        description=payload.description,
    )


@router.get('/offers', response_model=MarketOfferListResponse)
def list_market_offers(
    listing_id: int | None = Query(default=None, ge=1),
    status_value: str | None = Query(default=None, alias='status'),
    buyer_search: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return MarketplaceService(db).list_offers_for_user(
        user,
        listing_id=listing_id,
        status_value=status_value,
        buyer_search=buyer_search,
        limit=limit,
        offset=offset,
    )


@router.post('/offers', response_model=MarketOfferOut, status_code=201)
def create_market_offer(payload: MarketOfferCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MarketplaceService(db).create_offer_for_user(user=user, listing_id=payload.listing_id, buyer_name=payload.buyer_name, buyer_contact=payload.buyer_contact, offered_price=payload.offered_price, requested_quantity=payload.requested_quantity, message=payload.message, status_value=payload.status)


@router.patch('/offers/{offer_id}/status', response_model=MarketOfferOut)
def update_offer_status(offer_id: int, payload: MarketOfferStatusUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MarketplaceService(db).update_offer_status_for_user(user=user, offer_id=offer_id, status_value=payload.status)
