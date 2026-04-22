from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.quality import (
    CertificationCreateRequest,
    CertificationOut,
    QualityTestCreateRequest,
    QualityTestListResponse,
    QualityTestOut,
    QualityTestUpdateRequest,
)
from app.services.quality_service import QualityService

router = APIRouter()


@router.get('/tests', response_model=QualityTestListResponse)
def list_quality_tests(
    farm_id: int | None = Query(default=None, ge=1),
    plot_id: int | None = Query(default=None, ge=1),
    status_value: str | None = Query(default=None, alias='status'),
    test_type: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return QualityService(db).list_tests_for_user(
        user,
        farm_id=farm_id,
        plot_id=plot_id,
        status_value=status_value,
        test_type=test_type,
        limit=limit,
        offset=offset,
    )


@router.post('/tests', response_model=QualityTestOut, status_code=201)
def create_quality_test(payload: QualityTestCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return QualityService(db).create_test_for_user(
        user=user,
        farm_id=payload.farm_id,
        plot_id=payload.plot_id,
        harvest_id=payload.harvest_id,
        test_type=payload.test_type,
        result_value=payload.result_value,
        status_value=payload.status,
        tested_at=payload.tested_at,
    )


@router.get('/tests/{test_id}', response_model=QualityTestOut)
def get_quality_test(test_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return QualityService(db).get_test_for_user(user=user, test_id=test_id)


@router.patch('/tests/{test_id}', response_model=QualityTestOut)
def update_quality_test(test_id: int, payload: QualityTestUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return QualityService(db).update_test_for_user(
        user=user,
        test_id=test_id,
        result_value=payload.result_value,
        status_value=payload.status,
        tested_at=payload.tested_at,
    )


@router.get('/certifications', response_model=list[CertificationOut])
def list_certifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return QualityService(db).list_certifications_for_user(user)


@router.post('/certifications', response_model=CertificationOut, status_code=201)
def create_certification(payload: CertificationCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return QualityService(db).create_certification_for_user(
        user=user,
        farm_id=payload.farm_id,
        name=payload.name,
        issuer=payload.issuer,
        valid_until=payload.valid_until,
    )
