import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import decode_access_token
from app.db.session import SessionLocal, get_db
from app.models.iot_reading import IoTReading
from app.models.user import User
from app.schemas.iot import (
    IoTDeviceCreateRequest,
    IoTDeviceListResponse,
    IoTDeviceOut,
    IoTMetricSummaryListResponse,
    IoTReadingCreateRequest,
    IoTReadingListResponse,
    IoTReadingOut,
    IoTRuleAlertListResponse,
    IoTRuleCreateRequest,
    IoTRuleListResponse,
    IoTRuleOut,
    IoTValveCommandCreateRequest,
    IoTValveCommandListResponse,
    IoTValveCommandOut,
)
from app.services.iot_service import IoTService

router = APIRouter()


def _websocket_user_from_token(token: str, db: Session) -> User | None:
    try:
        payload = decode_access_token(token)
    except ValueError:
        return None
    subject = payload.get("sub")
    if not subject:
        return None
    try:
        user_id = int(subject)
    except (TypeError, ValueError):
        return None
    user = db.get(User, user_id)
    if not user:
        return None
    return user


def _websocket_token(websocket: WebSocket) -> str | None:
    auth_header = websocket.headers.get('authorization')
    if auth_header:
        lower = auth_header.lower()
        if lower.startswith('bearer '):
            return auth_header[7:].strip()
    return websocket.query_params.get('token')


@router.get('/devices', response_model=IoTDeviceListResponse)
def list_iot_devices(
    status_value: str | None = Query(default=None, alias='status'),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return IoTService(db).list_devices_for_user(user, status_value=status_value, limit=limit, offset=offset)


@router.post('/devices', response_model=IoTDeviceOut, status_code=201)
def create_iot_device(payload: IoTDeviceCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return IoTService(db).create_device_for_user(user=user, farm_id=payload.farm_id, plot_id=payload.plot_id, name=payload.name, device_type=payload.device_type, status_value=payload.status)


@router.get('/readings', response_model=IoTReadingListResponse)
def list_iot_readings(
    device_id: int | None = Query(default=None, ge=1),
    metric: str | None = Query(default=None),
    recorded_from: datetime | None = Query(default=None),
    recorded_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return IoTService(db).list_readings_for_user(
        user=user,
        device_id=device_id,
        metric=metric,
        recorded_from=recorded_from,
        recorded_to=recorded_to,
        limit=limit,
        offset=offset,
    )


@router.get('/readings/latest', response_model=list[IoTReadingOut])
def list_latest_iot_readings(
    limit: int = Query(default=50, ge=1, le=500),
    device_id: int | None = Query(default=None, ge=1),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return IoTService(db).list_latest_readings_for_user(user=user, limit=limit, device_id=device_id)


@router.get('/readings/metrics-summary', response_model=IoTMetricSummaryListResponse)
def get_iot_metrics_summary(
    device_id: int | None = Query(default=None, ge=1),
    recorded_from: datetime | None = Query(default=None),
    recorded_to: datetime | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return IoTService(db).metrics_summary_for_user(
        user=user,
        device_id=device_id,
        recorded_from=recorded_from,
        recorded_to=recorded_to,
    )




@router.get('/rules', response_model=IoTRuleListResponse)
def list_iot_rules(
    farm_id: int | None = Query(default=None, ge=1),
    status_value: str | None = Query(default=None, alias='status'),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return IoTService(db).list_rules_for_user(user=user, farm_id=farm_id, status_value=status_value, limit=limit, offset=offset)


@router.post('/rules', response_model=IoTRuleOut, status_code=201)
def create_iot_rule(payload: IoTRuleCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return IoTService(db).create_rule_for_user(
        user=user,
        farm_id=payload.farm_id,
        device_id=payload.device_id,
        metric=payload.metric,
        operator=payload.operator,
        threshold_value=payload.threshold_value,
        severity=payload.severity,
        status_value=payload.status,
    )


@router.get('/alerts', response_model=IoTRuleAlertListResponse)
def list_iot_alerts(
    farm_id: int | None = Query(default=None, ge=1),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return IoTService(db).list_alerts_for_user(user=user, farm_id=farm_id, limit=limit, offset=offset)



@router.get('/valves/commands', response_model=IoTValveCommandListResponse)
def list_iot_valve_commands(
    farm_id: int | None = Query(default=None, ge=1),
    device_id: int | None = Query(default=None, ge=1),
    status_value: str | None = Query(default=None, alias='status'),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return IoTService(db).list_valve_commands_for_user(
        user=user,
        farm_id=farm_id,
        device_id=device_id,
        status_value=status_value,
        limit=limit,
        offset=offset,
    )


@router.post('/valves/commands', response_model=IoTValveCommandOut, status_code=201)
def create_iot_valve_command(payload: IoTValveCommandCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return IoTService(db).create_valve_command_for_user(
        user=user,
        farm_id=payload.farm_id,
        device_id=payload.device_id,
        action=payload.action,
        source=payload.source,
    )

@router.post('/readings', response_model=IoTReadingOut, status_code=201)
def create_iot_reading(payload: IoTReadingCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return IoTService(db).create_reading_for_user(user=user, device_id=payload.device_id, metric=payload.metric, value=payload.value, unit=payload.unit, recorded_at=payload.recorded_at)


@router.websocket('/readings/stream')
async def stream_iot_readings(websocket: WebSocket):
    token = _websocket_token(websocket)
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason='Falta token (Bearer o query param)')
        return

    db = SessionLocal()
    user = _websocket_user_from_token(token, db)
    if user is None:
        db.close()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason='Token inválido')
        return

    await websocket.accept()
    limit_raw = websocket.query_params.get('limit')
    device_raw = websocket.query_params.get('device_id')
    try:
        limit = int(limit_raw) if limit_raw is not None else 10
        device_id = int(device_raw) if device_raw is not None else None
    except ValueError:
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA, reason='Parámetros inválidos')
        db.close()
        return
    if limit < 1 or limit > 500:
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA, reason='limit debe estar entre 1 y 500')
        db.close()
        return
    if device_id is not None and device_id < 1:
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA, reason='device_id inválido')
        db.close()
        return

    service = IoTService(db)
    last_sent_id = 0

    try:
        while True:
            try:
                readings = service.list_latest_readings_for_user(user=user, limit=limit, device_id=device_id)
            except HTTPException as exc:
                await websocket.send_json({"type": "error", "detail": exc.detail, "status_code": exc.status_code})
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason='Acceso denegado')
                return
            payload = []
            for reading in readings:
                if isinstance(reading, IoTReading) and reading.id > last_sent_id:
                    payload.append(IoTReadingOut.model_validate(reading).model_dump(mode='json'))
            if payload:
                last_sent_id = max(item['id'] for item in payload)
                await websocket.send_json({"type": "iot_readings", "items": payload})
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
    finally:
        db.close()
