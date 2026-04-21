from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.iot_repository import IoTRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.iot import (
    IoTDeviceListResponse,
    IoTMetricSummaryListResponse,
    IoTMetricSummaryOut,
    IoTReadingListResponse,
    IoTRuleAlertListResponse,
    IoTRuleAlertOut,
    IoTRuleListResponse,
    IoTValveCommandListResponse,
)


class IoTService:
    VALID_OPERATORS = {'>', '>=', '<', '<=', '=='}
    VALID_VALVE_ACTIONS = {'open', 'close', 'pulse'}

    def __init__(self, db: Session):
        self.db = db
        self.iot = IoTRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_devices_for_user(self, user: User, *, status_value: str | None = None, limit: int = 100, offset: int = 0) -> IoTDeviceListResponse:
        if limit < 1 or limit > 500:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='El parámetro limit debe estar entre 1 y 500')
        if offset < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='El parámetro offset debe ser mayor o igual a 0')
        total, items = self.iot.list_devices_by_farm_ids(
            self.relations.list_farm_ids_by_user(user.id),
            status_value=status_value,
            limit=limit,
            offset=offset,
        )
        return IoTDeviceListResponse(total=total, items=items)

    def create_device_for_user(self, *, user: User, farm_id: int, plot_id: int | None, name: str, device_type: str, status_value: str):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        device = self.iot.create_device(farm_id=farm_id, plot_id=plot_id, name=name, device_type=device_type, status=status_value)
        self.audit.add(module='iot', action='create_device', user_id=user.id, farm_id=farm_id, record_id=str(device.id))
        self.db.commit(); self.db.refresh(device)
        return device

    def list_readings_for_user(
        self,
        *,
        user: User,
        device_id: int | None = None,
        metric: str | None = None,
        recorded_from: datetime | None = None,
        recorded_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> IoTReadingListResponse:
        if limit < 1 or limit > 500:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='El parámetro limit debe estar entre 1 y 500')
        if offset < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='El parámetro offset debe ser mayor o igual a 0')
        if recorded_from is not None and recorded_to is not None and recorded_from > recorded_to:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='Rango de fechas inválido')

        devices = self.iot.list_devices_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))[1]
        allowed_device_ids = [d.id for d in devices]
        if device_id is not None and device_id not in allowed_device_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a este dispositivo')

        total, items = self.iot.list_readings_by_device_ids(
            allowed_device_ids,
            device_id=device_id,
            metric=metric,
            recorded_from=recorded_from,
            recorded_to=recorded_to,
            limit=limit,
            offset=offset,
        )
        return IoTReadingListResponse(total=total, items=items)

    def list_latest_readings_for_user(self, *, user: User, limit: int = 50, device_id: int | None = None):
        if limit < 1 or limit > 500:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='El parámetro limit debe estar entre 1 y 500')
        devices = self.iot.list_devices_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))[1]
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

    def metrics_summary_for_user(
        self,
        *,
        user: User,
        device_id: int | None = None,
        recorded_from: datetime | None = None,
        recorded_to: datetime | None = None,
    ) -> IoTMetricSummaryListResponse:
        if recorded_from is not None and recorded_to is not None and recorded_from > recorded_to:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='Rango de fechas inválido')

        devices = self.iot.list_devices_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))[1]
        allowed_device_ids = [d.id for d in devices]
        if device_id is not None and device_id not in allowed_device_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a este dispositivo')

        rows = self.iot.metric_summary_by_device_ids(
            allowed_device_ids,
            device_id=device_id,
            recorded_from=recorded_from,
            recorded_to=recorded_to,
        )
        items = [
            IoTMetricSummaryOut(
                metric=metric,
                count=count,
                min_value=min_value,
                max_value=max_value,
                avg_value=avg_value,
            )
            for metric, count, min_value, max_value, avg_value in rows
        ]
        return IoTMetricSummaryListResponse(total_metrics=len(items), items=items)

    def create_rule_for_user(
        self,
        *,
        user: User,
        farm_id: int,
        device_id: int | None,
        metric: str,
        operator: str,
        threshold_value: float,
        severity: str,
        status_value: str,
    ):
        if operator not in self.VALID_OPERATORS:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='Operador inválido')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        if device_id is not None:
            device = self.iot.get_device(device_id)
            if device is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Dispositivo no encontrado')
            if device.farm_id != farm_id:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='El dispositivo no pertenece a la finca')

        rule = self.iot.create_rule(
            farm_id=farm_id,
            device_id=device_id,
            metric=metric,
            operator=operator,
            threshold_value=threshold_value,
            severity=severity,
            status=status_value,
        )
        self.audit.add(module='iot', action='create_rule', user_id=user.id, farm_id=farm_id, record_id=str(rule.id))
        self.db.commit(); self.db.refresh(rule)
        return rule

    def list_rules_for_user(
        self,
        *,
        user: User,
        farm_id: int | None = None,
        status_value: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> IoTRuleListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.iot.list_rules_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            status_value=status_value,
            limit=limit,
            offset=offset,
        )
        return IoTRuleListResponse(total=total, items=items)

    def list_alerts_for_user(
        self,
        *,
        user: User,
        farm_id: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> IoTRuleAlertListResponse:
        rules_payload = self.list_rules_for_user(user=user, farm_id=farm_id, status_value='active', limit=limit, offset=offset)
        devices = self.iot.list_devices_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))[1]
        allowed_device_ids = [d.id for d in devices]
        alerts: list[IoTRuleAlertOut] = []

        for rule in rules_payload.items:
            reading = self.iot.latest_reading_for_rule(rule=rule, allowed_device_ids=allowed_device_ids)
            if reading is None:
                continue
            if self._triggered(float(reading.value), rule.operator, float(rule.threshold_value)):
                alerts.append(
                    IoTRuleAlertOut(
                        rule_id=rule.id,
                        farm_id=rule.farm_id,
                        device_id=reading.device_id,
                        metric=rule.metric,
                        operator=rule.operator,
                        threshold_value=float(rule.threshold_value),
                        current_value=float(reading.value),
                        severity=rule.severity,
                        triggered_at=reading.recorded_at,
                    )
                )

        return IoTRuleAlertListResponse(total=len(alerts), items=alerts)

    def _triggered(self, current_value: float, operator: str, threshold: float) -> bool:
        if operator == '>':
            return current_value > threshold
        if operator == '>=':
            return current_value >= threshold
        if operator == '<':
            return current_value < threshold
        if operator == '<=':
            return current_value <= threshold
        return current_value == threshold


    def create_valve_command_for_user(
        self,
        *,
        user: User,
        farm_id: int,
        device_id: int,
        action: str,
        source: str,
    ):
        if action not in self.VALID_VALVE_ACTIONS:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='Acción de válvula inválida')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')

        device = self.iot.get_device(device_id)
        if device is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Dispositivo no encontrado')
        if device.farm_id != farm_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='El dispositivo no pertenece a la finca')

        command = self.iot.create_valve_command(
            farm_id=farm_id,
            device_id=device_id,
            action=action,
            source=source,
        )
        self.audit.add(module='iot', action='create_valve_command', user_id=user.id, farm_id=farm_id, record_id=str(command.id))
        self.db.commit(); self.db.refresh(command)
        return command

    def list_valve_commands_for_user(
        self,
        *,
        user: User,
        farm_id: int | None = None,
        device_id: int | None = None,
        status_value: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> IoTValveCommandListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.iot.list_valve_commands_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            device_id=device_id,
            status_value=status_value,
            limit=limit,
            offset=offset,
        )
        return IoTValveCommandListResponse(total=total, items=items)
