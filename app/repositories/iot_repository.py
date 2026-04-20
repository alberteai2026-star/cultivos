from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.iot_device import IoTDevice
from app.models.iot_reading import IoTReading


class IoTRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_device(self, *, farm_id: int, plot_id: int | None, name: str, device_type: str, status: str) -> IoTDevice:
        device = IoTDevice(farm_id=farm_id, plot_id=plot_id, name=name, device_type=device_type, status=status)
        self.db.add(device)
        self.db.flush()
        return device

    def list_devices_by_farm_ids(self, farm_ids: list[int]) -> list[IoTDevice]:
        if not farm_ids:
            return []
        q = select(IoTDevice).where(IoTDevice.farm_id.in_(farm_ids)).order_by(IoTDevice.id.desc())
        return list(self.db.scalars(q).all())

    def get_device(self, device_id: int) -> IoTDevice | None:
        return self.db.get(IoTDevice, device_id)

    def create_reading(self, *, device_id: int, metric: str, value: float, unit: str | None, recorded_at: datetime) -> IoTReading:
        reading = IoTReading(device_id=device_id, metric=metric, value=value, unit=unit, recorded_at=recorded_at)
        self.db.add(reading)
        self.db.flush()
        return reading

    def list_readings_by_device_ids(self, device_ids: list[int], *, limit: int | None = None, offset: int = 0) -> list[IoTReading]:
        if not device_ids:
            return []
        q = select(IoTReading).where(IoTReading.device_id.in_(device_ids)).order_by(IoTReading.recorded_at.desc(), IoTReading.id.desc())
        if offset:
            q = q.offset(offset)
        if limit is not None:
            q = q.limit(limit)
        return list(self.db.scalars(q).all())

    def list_latest_readings_by_device_ids(self, device_ids: list[int], *, limit: int, device_id: int | None = None) -> list[IoTReading]:
        if not device_ids:
            return []
        q = select(IoTReading).where(IoTReading.device_id.in_(device_ids))
        if device_id is not None:
            q = q.where(IoTReading.device_id == device_id)
        q = q.order_by(IoTReading.recorded_at.desc(), IoTReading.id.desc()).limit(limit)
        return list(self.db.scalars(q).all())
