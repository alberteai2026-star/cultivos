from fastapi import FastAPI

from app.api.v1.ai import router as ai_router
from app.api.v1.audit import router as audit_router
from app.api.v1.auth import router as auth_router
from app.api.v1.billing import router as billing_router
from app.api.v1.crop_cycles import router as crop_cycles_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.farms import router as farms_router
from app.api.v1.finance import router as finance_router
from app.api.v1.gis import router as gis_router
from app.api.v1.harvests import router as harvests_router
from app.api.v1.health import router as health_router
from app.api.v1.inputs import router as inputs_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.iot import router as iot_router
from app.api.v1.irrigation import router as irrigation_router
from app.api.v1.logistics import router as logistics_router
from app.api.v1.machines import router as machines_router
from app.api.v1.marketplace import router as marketplace_router
from app.api.v1.monitoring import router as monitoring_router
from app.api.v1.nursery import router as nursery_router
from app.api.v1.phytosanitary import router as phytosanitary_router
from app.api.v1.plots import router as plots_router
from app.api.v1.quality import router as quality_router
from app.api.v1.reports import router as reports_router
from app.api.v1.rotation import router as rotation_router
from app.api.v1.settings import router as settings_router
from app.api.v1.security import router as security_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.weather import router as weather_router
from app.api.v1.workers import router as workers_router
from app.core.config import settings

base = settings.api_v1_prefix

ROUTER_REGISTRY = [
    (health_router, base, ["health"]),
    (auth_router, f"{base}/auth", ["auth"]),
    (farms_router, f"{base}/farms", ["farms"]),
    (plots_router, f"{base}/plots", ["plots"]),
    (crop_cycles_router, f"{base}/crop-cycles", ["crop-cycles"]),
    (tasks_router, f"{base}/tasks", ["tasks"]),
    (inputs_router, f"{base}/inputs", ["inputs"]),
    (harvests_router, f"{base}/harvests", ["harvests"]),
    (monitoring_router, f"{base}/monitoring", ["monitoring"]),
    (weather_router, f"{base}/weather", ["weather"]),
    (irrigation_router, f"{base}/irrigation", ["irrigation"]),
    (rotation_router, f"{base}/rotation", ["rotation"]),
    (workers_router, f"{base}/workers", ["workers"]),
    (machines_router, f"{base}/machines", ["machines"]),
    (inventory_router, f"{base}/inventory", ["inventory"]),
    (quality_router, f"{base}/quality", ["quality"]),
    (nursery_router, f"{base}/nursery", ["nursery"]),
    (phytosanitary_router, f"{base}/phytosanitary", ["phytosanitary"]),
    (finance_router, f"{base}/finance", ["finance"]),
    (billing_router, f"{base}/billing", ["billing"]),
    (logistics_router, f"{base}/logistics", ["logistics"]),
    (marketplace_router, f"{base}/marketplace", ["marketplace"]),
    (reports_router, f"{base}/reports", ["reports"]),
    (ai_router, f"{base}/ai", ["ai"]),
    (audit_router, f"{base}/audit", ["audit"]),
    (settings_router, f"{base}/settings", ["settings"]),
    (dashboard_router, f"{base}/dashboard", ["dashboard"]),
    (gis_router, f"{base}/gis", ["gis"]),
    (iot_router, f"{base}/iot", ["iot"]),
    (security_router, f"{base}/security", ["security"]),
]


def include_all_routers(app: FastAPI) -> None:
    for router, prefix, tags in ROUTER_REGISTRY:
        app.include_router(router, prefix=prefix, tags=tags)
