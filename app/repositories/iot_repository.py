from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.iot_device import IoTDevice
from app.models.iot_reading import IoTReading
from app.models.iot_rule import IoTRule
from app.models.iot_valve_command import IoTValveCommand


class IoTRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_device(self, *, farm_id: int, plot_id: int | None, name: str, device_type: str, status: str) -> IoTDevice:
        device = IoTDevice(farm_id=farm_id, plot_id=plot_id, name=name, device_type=device_type, status=status)
        self.db.add(device)
        self.db.flush()
        return device

    def list_devices_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        status_value: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[IoTDevice]]:
        if not farm_ids:
            return 0, []
        q = select(IoTDevice).where(IoTDevice.farm_id.in_(farm_ids))
        count_q = select(func.count(IoTDevice.id)).where(IoTDevice.farm_id.in_(farm_ids))
        if status_value is not None:
            q = q.where(IoTDevice.status == status_value)
            count_q = count_q.where(IoTDevice.status == status_value)
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(IoTDevice.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_device(self, device_id: int) -> IoTDevice | None:
        return self.db.get(IoTDevice, device_id)

    def create_reading(self, *, device_id: int, metric: str, value: float, unit: str | None, recorded_at: datetime) -> IoTReading:
        reading = IoTReading(device_id=device_id, metric=metric, value=value, unit=unit, recorded_at=recorded_at)
        self.db.add(reading)
        self.db.flush()
        return reading

    def list_readings_by_device_ids(
        self,
        device_ids: list[int],
        *,
        device_id: int | None = None,
        metric: str | None = None,
        recorded_from: datetime | None = None,
        recorded_to: datetime | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> tuple[int, list[IoTReading]]:
        if not device_ids:
            return 0, []
        q = select(IoTReading).where(IoTReading.device_id.in_(device_ids))
        count_q = select(func.count(IoTReading.id)).where(IoTReading.device_id.in_(device_ids))

        if device_id is not None:
            q = q.where(IoTReading.device_id == device_id)
            count_q = count_q.where(IoTReading.device_id == device_id)
        if metric is not None:
            q = q.where(IoTReading.metric == metric)
            count_q = count_q.where(IoTReading.metric == metric)
        if recorded_from is not None:
            q = q.where(IoTReading.recorded_at >= recorded_from)
            count_q = count_q.where(IoTReading.recorded_at >= recorded_from)
        if recorded_to is not None:
            q = q.where(IoTReading.recorded_at <= recorded_to)
            count_q = count_q.where(IoTReading.recorded_at <= recorded_to)

        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(IoTReading.recorded_at.desc(), IoTReading.id.desc())
        if offset:
            q = q.offset(offset)
        if limit is not None:
            q = q.limit(limit)
        return total, list(self.db.scalars(q).all())

    def list_latest_readings_by_device_ids(self, device_ids: list[int], *, limit: int, device_id: int | None = None) -> list[IoTReading]:
        if not device_ids:
            return []
        q = select(IoTReading).where(IoTReading.device_id.in_(device_ids))
        if device_id is not None:
            q = q.where(IoTReading.device_id == device_id)
        q = q.order_by(IoTReading.recorded_at.desc(), IoTReading.id.desc()).limit(limit)
        return list(self.db.scalars(q).all())

    def metric_summary_by_device_ids(
        self,
        device_ids: list[int],
        *,
        device_id: int | None = None,
        recorded_from: datetime | None = None,
        recorded_to: datetime | None = None,
    ) -> list[tuple[str, int, float, float, float]]:
        if not device_ids:
            return []

        q = (
            select(
                IoTReading.metric,
                func.count(IoTReading.id),
                func.min(IoTReading.value),
                func.max(IoTReading.value),
                func.avg(IoTReading.value),
            )
            .where(IoTReading.device_id.in_(device_ids))
            .group_by(IoTReading.metric)
            .order_by(func.count(IoTReading.id).desc(), IoTReading.metric.asc())
        )
        if device_id is not None:
            q = q.where(IoTReading.device_id == device_id)
        if recorded_from is not None:
            q = q.where(IoTReading.recorded_at >= recorded_from)
        if recorded_to is not None:
            q = q.where(IoTReading.recorded_at <= recorded_to)

        rows = self.db.execute(q).all()
        return [
            (str(metric), int(count), float(min_v), float(max_v), float(avg_v))
            for metric, count, min_v, max_v, avg_v in rows
        ]

    def create_rule(
        self,
        *,
        farm_id: int,
        device_id: int | None,
        metric: str,
        operator: str,
        threshold_value: float,
        severity: str,
        status: str,
    ) -> IoTRule:
        rule = IoTRule(
            farm_id=farm_id,
            device_id=device_id,
            metric=metric,
            operator=operator,
            threshold_value=threshold_value,
            severity=severity,
            status=status,
        )
        self.db.add(rule)
        self.db.flush()
        return rule

    def list_rules_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        status_value: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[IoTRule]]:
        if not farm_ids:
            return 0, []
        q = select(IoTRule).where(IoTRule.farm_id.in_(farm_ids))
        count_q = select(func.count(IoTRule.id)).where(IoTRule.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(IoTRule.farm_id == farm_id)
            count_q = count_q.where(IoTRule.farm_id == farm_id)
        if status_value is not None:
            q = q.where(IoTRule.status == status_value)
            count_q = count_q.where(IoTRule.status == status_value)
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(IoTRule.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def latest_reading_for_rule(self, *, rule: IoTRule, allowed_device_ids: list[int]) -> IoTReading | None:
        if not allowed_device_ids:
            return None
        q = select(IoTReading).where(IoTReading.device_id.in_(allowed_device_ids), IoTReading.metric == rule.metric)
        if rule.device_id is not None:
            q = q.where(IoTReading.device_id == rule.device_id)
        q = q.order_by(IoTReading.recorded_at.desc(), IoTReading.id.desc()).limit(1)
        return self.db.scalar(q)


    def create_valve_command(
        self,
        *,
        farm_id: int,
        device_id: int,
        action: str,
        source: str,
    ) -> IoTValveCommand:
        command = IoTValveCommand(
            farm_id=farm_id,
            device_id=device_id,
            action=action,
            source=source,
            status='queued',
        )
        self.db.add(command)
        self.db.flush()
        return command

    def list_valve_commands_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        device_id: int | None = None,
        status_value: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[IoTValveCommand]]:
        if not farm_ids:
            return 0, []
        q = select(IoTValveCommand).where(IoTValveCommand.farm_id.in_(farm_ids))
        count_q = select(func.count(IoTValveCommand.id)).where(IoTValveCommand.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(IoTValveCommand.farm_id == farm_id)
            count_q = count_q.where(IoTValveCommand.farm_id == farm_id)
        if device_id is not None:
            q = q.where(IoTValveCommand.device_id == device_id)
            count_q = count_q.where(IoTValveCommand.device_id == device_id)
        if status_value is not None:
            q = q.where(IoTValveCommand.status == status_value)
            count_q = count_q.where(IoTValveCommand.status == status_value)
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(IoTValveCommand.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())
