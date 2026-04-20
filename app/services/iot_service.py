from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.iot_repository import IoTRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class IoTService:
    def __init__(self, db: Session):
        self.db = db
        self.iot = IoTRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_devices_for_user(self, user: User):
        return self.iot.list_devices_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))

    def create_device_for_user(self, *, user: User, farm_id: int, plot_id: int | None, name: str, device_type: str, status_value: str):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        device = self.iot.create_device(farm_id=farm_id, plot_id=plot_id, name=name, device_type=device_type, status=status_value)
        self.audit.add(module='iot', action='create_device', user_id=user.id, farm_id=farm_id, record_id=str(device.id))
        self.db.commit(); self.db.refresh(device)
        return device

    def list_readings_for_user(self, *, user: User, limit: int = 100, offset: int = 0):
        if limit < 1 or limit > 500:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El parámetro limit debe estar entre 1 y 500')
        if offset < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El parámetro offset debe ser mayor o igual a 0')
        devices = self.iot.list_devices_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))
        return self.iot.list_readings_by_device_ids([d.id for d in devices], limit=limit, offset=offset)

    def list_latest_readings_for_user(self, *, user: User, limit: int = 50, device_id: int | None = None):
        if limit < 1 or limit > 500:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El parámetro limit debe estar entre 1 y 500')
        devices = self.iot.list_devices_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))
        allowed_device_ids = [d.id for d in devices]
        if device_id is not None and device_id not in allowed_device_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a este dispositivo')
        return self.iot.list_latest_readings_by_device_ids(allowed_device_ids, limit=limit, device_id=device_id)

    def create_reading_for_user(self, *, user: User, device_id: int, metric: str, value: float, unit: str | None, recorded_at: datetime):
        device = self.iot.get_device(device_id)
        if device is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Dispositivo no encontrado')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=device.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a este dispositivo')
        reading = self.iot.create_reading(device_id=device_id, metric=metric, value=value, unit=unit, recorded_at=recorded_at)
        self.audit.add(module='iot', action='create_reading', user_id=user.id, farm_id=device.farm_id, record_id=str(reading.id))
        self.db.commit(); self.db.refresh(reading)
        return reading
