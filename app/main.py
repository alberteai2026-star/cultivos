from fastapi import FastAPI

from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.farms import router as farms_router
from app.api.v1.plots import router as plots_router
from app.api.v1.crop_cycles import router as crop_cycles_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.inputs import router as inputs_router
from app.api.v1.harvests import router as harvests_router
from app.api.v1.monitoring import router as monitoring_router
from app.api.v1.weather import router as weather_router
from app.api.v1.irrigation import router as irrigation_router
from app.api.v1.rotation import router as rotation_router
from app.api.v1.workers import router as workers_router
from app.api.v1.machines import router as machines_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.quality import router as quality_router
from app.api.v1.nursery import router as nursery_router
from app.api.v1.phytosanitary import router as phytosanitary_router
from app.api.v1.finance import router as finance_router
from app.api.v1.billing import router as billing_router
from app.api.v1.logistics import router as logistics_router
from app.api.v1.marketplace import router as marketplace_router
from app.api.v1.reports import router as reports_router
from app.api.v1.ai import router as ai_router
from app.api.v1.audit import router as audit_router
from app.api.v1.settings import router as settings_router
from app.api.v1.dashboard import router as dashboard_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(farms_router, prefix="/api/v1/farms", tags=["farms"])
app.include_router(plots_router, prefix="/api/v1/plots", tags=["plots"])
app.include_router(crop_cycles_router, prefix="/api/v1/crop-cycles", tags=["crop-cycles"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(inputs_router, prefix="/api/v1/inputs", tags=["inputs"])
app.include_router(harvests_router, prefix="/api/v1/harvests", tags=["harvests"])
app.include_router(monitoring_router, prefix="/api/v1/monitoring", tags=["monitoring"])
app.include_router(weather_router, prefix="/api/v1/weather", tags=["weather"])
app.include_router(irrigation_router, prefix="/api/v1/irrigation", tags=["irrigation"])
app.include_router(rotation_router, prefix="/api/v1/rotation", tags=["rotation"])
app.include_router(workers_router, prefix="/api/v1/workers", tags=["workers"])
app.include_router(machines_router, prefix="/api/v1/machines", tags=["machines"])
app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["inventory"])
app.include_router(quality_router, prefix="/api/v1/quality", tags=["quality"])
app.include_router(nursery_router, prefix="/api/v1/nursery", tags=["nursery"])
app.include_router(phytosanitary_router, prefix="/api/v1/phytosanitary", tags=["phytosanitary"])
app.include_router(finance_router, prefix="/api/v1/finance", tags=["finance"])
app.include_router(billing_router, prefix="/api/v1/billing", tags=["billing"])
app.include_router(logistics_router, prefix="/api/v1/logistics", tags=["logistics"])
app.include_router(marketplace_router, prefix="/api/v1/marketplace", tags=["marketplace"])
app.include_router(reports_router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(ai_router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(audit_router, prefix="/api/v1/audit", tags=["audit"])
app.include_router(settings_router, prefix="/api/v1/settings", tags=["settings"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["dashboard"])
