from datetime import datetime

import pytest
from fastapi import HTTPException

from app.services.marketplace_service import MarketplaceService


class _User:
    def __init__(self, user_id: int):
        self.id = user_id


class _Listing:
    def __init__(self):
        now = datetime.utcnow()
        self.id = 7
        self.farm_id = 10
        self.title = 'Cafe verde'
        self.product_name = 'Cafe'
        self.quantity = 100.0
        self.unit = 'kg'
        self.unit_price = 12.5
        self.status = 'abierta'
        self.description = 'Lote disponible'
        self.published_at = now
        self.created_at = now


class _Offer:
    def __init__(self):
        now = datetime.utcnow()
        self.id = 5
        self.listing_id = 7
        self.buyer_name = 'Acopio Central'
        self.buyer_contact = 'acopio@example.com'
        self.offered_price = 11.0
        self.requested_quantity = 20.0
        self.message = 'Interesados en compra semanal'
        self.status = 'nueva'
        self.created_at = now


class _Repo:
    def __init__(self):
        self.listing = _Listing()
        self.offer = _Offer()
        self.last_listing_args = None
        self.last_offer_args = None

    def list_listings_by_farm_ids(self, farm_ids, **kwargs):
        self.last_listing_args = {'farm_ids': farm_ids, **kwargs}
        if kwargs.get('limit') == 100000:
            return 1, [self.listing]
        return 1, [self.listing]

    def get_listing(self, listing_id: int):
        return self.listing if listing_id == self.listing.id else None

    def update_listing_fields(self, listing, **kwargs):
        self.last_listing_args = kwargs
        return listing

    def list_offers_by_listing_ids(self, listing_ids, **kwargs):
        self.last_offer_args = {'listing_ids': listing_ids, **kwargs}
        return 1, [self.offer]

    def create_offer(self, **kwargs):
        return self.offer

    def get_offer(self, offer_id: int):
        return self.offer if offer_id == self.offer.id else None


class _RelationsAllow:
    def list_farm_ids_by_user(self, user_id: int):
        return [10]

    def user_has_farm(self, *, user_id: int, farm_id: int) -> bool:
        return farm_id == 10


class _RelationsDeny:
    def list_farm_ids_by_user(self, user_id: int):
        return []

    def user_has_farm(self, *, user_id: int, farm_id: int) -> bool:
        return False


class _Audit:
    def __init__(self):
        self.entries = []

    def add(self, **kwargs):
        self.entries.append(kwargs)


class _DB:
    def __init__(self):
        self.commits = 0

    def commit(self):
        self.commits += 1

    def refresh(self, _obj):
        return None


def test_list_listings_for_user_forwards_filters():
    service = MarketplaceService(db=None)
    repo = _Repo()
    service.market = repo
    service.relations = _RelationsAllow()

    start = datetime.utcnow()
    payload = service.list_listings_for_user(_User(1), farm_id=10, status_value='abierta', product_search='cafe', published_from=start, limit=20, offset=4)

    assert payload.total == 1
    assert len(payload.items) == 1
    assert repo.last_listing_args['farm_ids'] == [10]
    assert repo.last_listing_args['status_value'] == 'abierta'


def test_get_listing_for_user_denies_without_access():
    service = MarketplaceService(db=None)
    service.market = _Repo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.get_listing_for_user(user=_User(1), listing_id=7)

    assert exc.value.status_code == 403


def test_update_listing_for_user_audits_and_commits():
    db = _DB()
    service = MarketplaceService(db=db)
    service.market = _Repo()
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    updated = service.update_listing_for_user(user=_User(1), listing_id=7, title='Cafe premium', product_name=None, quantity=None, unit=None, unit_price=None, description='Oferta mejorada')

    assert updated.id == 7
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'update_listing'


def test_list_offers_for_user_forwards_filters():
    service = MarketplaceService(db=None)
    repo = _Repo()
    service.market = repo
    service.relations = _RelationsAllow()

    payload = service.list_offers_for_user(_User(1), listing_id=7, status_value='nueva', buyer_search='acopio', limit=10, offset=0)

    assert payload.total == 1
    assert len(payload.items) == 1
    assert repo.last_offer_args['listing_ids'] == [7]
    assert repo.last_offer_args['status_value'] == 'nueva'


def test_update_offer_status_for_user_updates_and_audits():
    db = _DB()
    service = MarketplaceService(db=db)
    service.market = _Repo()
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    updated = service.update_offer_status_for_user(user=_User(1), offer_id=5, status_value='aceptada')

    assert updated.status == 'aceptada'
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'update_offer_status'
