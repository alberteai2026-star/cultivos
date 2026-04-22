# Cultivos API (Inicio)

Base inicial del sistema integral de cultivos.

## Stack elegido
- **Backend:** FastAPI (Python 3.10+)
- **ORM:** SQLAlchemy 2.x
- **Base de datos:** MySQL 8.0
- **Autenticación:** JWT (estructura base)
- **Infra local:** MySQL instalado localmente (sin Docker)

## Módulos iniciales implementados (estructura)
- M1: Autenticación/Usuarios (base)
- M2: Fincas (base)
- Auditoría (base)


## Setup rápido de desarrollo
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

## Ejecutar pruebas
```bash
pytest -q
```

## Guía para iniciar frontend

Antes de arrancar UI, revisar `docs/FRONTEND_READINESS.md` (checklist de brechas, orden recomendado y criterios Go/No-Go).

> Nota: CI en GitHub Actions ejecuta `pytest -q` en Python 3.10 y 3.11 para validar el scaffold en cada push/PR.

## Ejecutar local (cuando instales dependencias)
```bash
uv run uvicorn app.main:app --reload
```

## Endpoints iniciales funcionales
- `GET /api/v1/health` (retorna `status`, `service`, `version`, `environment`, `timestamp`)
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh` (recibe refresh token y retorna nuevo par de tokens)
- `GET /api/v1/auth/me` (requiere Bearer token, retorna el usuario autenticado)
- `GET /api/v1/farms/` (requiere Bearer token, listado paginado con `search`, `limit`, `offset`)
- `POST /api/v1/farms/` (requiere Bearer token, crea finca y asigna rol dueño)
- `GET /api/v1/farms/{farm_id}` (requiere Bearer token, detalle de finca autorizada)
- `PATCH /api/v1/farms/{farm_id}` (solo rol dueño, actualiza datos base de finca)
- `GET /api/v1/plots/` (requiere Bearer token, listado paginado con filtros `farm_id`, `search`, `status`)
- `POST /api/v1/plots/` (requiere Bearer token, valida acceso a finca y unicidad de código)
- `GET /api/v1/plots/{plot_id}` (requiere Bearer token, detalle de lote autorizado)
- `PATCH /api/v1/plots/{plot_id}` (requiere Bearer token, actualiza lote autorizado)
- `GET /api/v1/crop-cycles/` (requiere Bearer token, listado paginado con filtros por finca/lote/estado/especie/rango de siembra)
- `POST /api/v1/crop-cycles/` (requiere Bearer token, crea ciclo en lote autorizado)
- `GET /api/v1/crop-cycles/{cycle_id}` (requiere Bearer token, detalle de ciclo autorizado)
- `PATCH /api/v1/crop-cycles/{cycle_id}` (requiere Bearer token, actualiza datos del ciclo)
- `PATCH /api/v1/crop-cycles/{cycle_id}/status` (requiere Bearer token, transición de estado controlada)
- `GET /api/v1/tasks/` (requiere Bearer token, listado paginado con filtros por finca/lote/estado/búsqueda/rango de fecha)
- `POST /api/v1/tasks/` (requiere Bearer token, crea labor en lote autorizado)
- `GET /api/v1/tasks/{task_id}` (requiere Bearer token, detalle de labor autorizada)
- `PATCH /api/v1/tasks/{task_id}` (requiere Bearer token, actualiza campos de labor)
- `PATCH /api/v1/tasks/{task_id}/status` (requiere Bearer token, cambia estado de labor)
- `GET /api/v1/inputs/products` (requiere Bearer token, listado paginado con filtros `search`, `category`)
- `POST /api/v1/inputs/products` (requiere Bearer token, crea insumo)
- `GET /api/v1/inputs/products/{product_id}` (requiere Bearer token, detalle de insumo)
- `PATCH /api/v1/inputs/products/{product_id}` (requiere Bearer token, actualiza insumo)
- `GET /api/v1/inputs/applications` (requiere Bearer token, listado paginado con filtros por finca/lote/insumo/rango de aplicación)
- `POST /api/v1/inputs/applications` (requiere Bearer token, registra aplicación de insumo)
- `GET /api/v1/inputs/applications/{application_id}` (requiere Bearer token, detalle de aplicación autorizada)
- `PATCH /api/v1/inputs/applications/{application_id}` (requiere Bearer token, actualiza aplicación autorizada)
- `GET /api/v1/harvests/` (requiere Bearer token, listado paginado con filtros por finca/lote/ciclo/rango de fecha de cosecha)
- `POST /api/v1/harvests/` (requiere Bearer token, registra cosecha en lote autorizado)
- `GET /api/v1/harvests/{harvest_id}` (requiere Bearer token, detalle de cosecha autorizada)
- `PATCH /api/v1/harvests/{harvest_id}` (requiere Bearer token, actualiza campos de cosecha)
- `GET /api/v1/monitoring/visits` (requiere Bearer token, listado paginado con filtros por finca/lote/ciclo/afectación/severidad/rango de fecha)
- `POST /api/v1/monitoring/visits` (requiere Bearer token, registra visita de monitoreo)
- `GET /api/v1/monitoring/visits/{visit_id}` (requiere Bearer token, detalle de visita autorizada)
- `PATCH /api/v1/monitoring/visits/{visit_id}` (requiere Bearer token, actualiza datos de visita)
- `GET /api/v1/weather/observations` (requiere Bearer token, listado paginado con filtros por finca/fuente/rango de fecha)
- `GET /api/v1/weather/observations/{observation_id}` (requiere Bearer token, detalle de observación autorizada)
- `GET /api/v1/iot/devices` (paginado con filtros por `status`)
- `GET /api/v1/iot/readings` (paginado con filtros por `device_id`, `metric`, rango `recorded_from/recorded_to`)
- `GET /api/v1/iot/readings/metrics-summary` (agregados por métrica: count/min/max/avg)
- `GET /api/v1/iot/rules` (listado paginado de reglas IoT por finca/estado)
- `POST /api/v1/iot/rules` (crea regla de automatización/alerta IoT por métrica y umbral)
- `GET /api/v1/iot/alerts` (alertas IoT activas evaluadas contra la lectura más reciente)
- `GET /api/v1/iot/valves/commands` (listado paginado de comandos de electroválvulas)
- `GET /api/v1/security/incidents` (listado paginado de incidentes de seguridad perimetral)
- `POST /api/v1/security/incidents` (crea incidente de seguridad en finca autorizada)
- `GET /api/v1/security/incidents/{incident_id}` (detalle de incidente autorizado)
- `PATCH /api/v1/security/incidents/{incident_id}/status` (actualiza estado/cierre de incidente de seguridad)
- `POST /api/v1/iot/valves/commands` (envía comando manual de electroválvula: open/close/pulse)
- `POST /api/v1/weather/observations` (requiere Bearer token, registra observación climática)
- `PATCH /api/v1/weather/observations/{observation_id}` (requiere Bearer token, actualiza observación climática)
- `GET /api/v1/irrigation/events` (requiere Bearer token, listado paginado con filtros por finca/lote/estado/rango)
- `POST /api/v1/irrigation/events` (requiere Bearer token, crea evento de riego)
- `GET /api/v1/irrigation/events/{event_id}` (requiere Bearer token, detalle de evento autorizado)
- `PATCH /api/v1/irrigation/events/{event_id}` (requiere Bearer token, actualiza evento autorizado)
- `PATCH /api/v1/irrigation/events/{event_id}/status` (requiere Bearer token, cambia estado con transición controlada)
- `GET /api/v1/rotation/plans` (requiere Bearer token, listado paginado con filtros por finca/lote/estado/especie)
- `POST /api/v1/rotation/plans` (requiere Bearer token, crea plan de rotación)
- `GET /api/v1/rotation/plans/{plan_id}` (requiere Bearer token, detalle de plan autorizado)
- `PATCH /api/v1/rotation/plans/{plan_id}` (requiere Bearer token, actualiza plan autorizado)
- `PATCH /api/v1/rotation/plans/{plan_id}/status` (requiere Bearer token, cambia estado del plan)
- `GET /api/v1/workers/` (requiere Bearer token, listado paginado con filtros por finca/estado/búsqueda)
- `POST /api/v1/workers/` (requiere Bearer token, crea trabajador)
- `GET /api/v1/workers/{worker_id}` (requiere Bearer token, detalle de trabajador autorizado)
- `PATCH /api/v1/workers/{worker_id}` (requiere Bearer token, actualiza trabajador autorizado)
- `PATCH /api/v1/workers/{worker_id}/status` (requiere Bearer token, activa/inactiva trabajador)
- `POST /api/v1/workers/{worker_id}/tracking` (registra ubicación de trabajador en campo)
- `GET /api/v1/workers/{worker_id}/tracking` (historial de ubicaciones del trabajador con filtros por rango)
- `GET /api/v1/machines/` (requiere Bearer token, listado paginado con filtros por finca/estado/búsqueda)
- `POST /api/v1/machines/` (requiere Bearer token, crea máquina)
- `GET /api/v1/machines/{machine_id}` (requiere Bearer token, detalle de máquina autorizada)
- `PATCH /api/v1/machines/{machine_id}` (requiere Bearer token, actualiza máquina autorizada)
- `PATCH /api/v1/machines/{machine_id}/status` (requiere Bearer token, cambia estado de máquina)
- `GET /api/v1/finance/entries` (requiere Bearer token, listado de entradas financieras autorizadas)
- `POST /api/v1/finance/entries` (requiere Bearer token, registra ingreso/costo financiero)
- `GET /api/v1/finance/summary` (requiere Bearer token, resumen financiero por finca y rango)
- `POST /api/v1/finance/journal-entries` (crea asiento contable NIIF balanceado)
- `GET /api/v1/finance/journal-entries` (listado paginado de asientos contables NIIF)
- `GET /api/v1/finance/trial-balance` (balance de comprobación por finca y rango)
- `GET /api/v1/logistics/shipments` (requiere Bearer token, listado paginado con filtros por finca/estado/destino/rango de salida)
- `POST /api/v1/logistics/shipments` (requiere Bearer token, crea despacho logístico)
- `GET /api/v1/logistics/shipments/{shipment_id}` (requiere Bearer token, detalle de despacho autorizado)
- `PATCH /api/v1/logistics/shipments/{shipment_id}` (requiere Bearer token, actualiza despacho autorizado)
- `PATCH /api/v1/logistics/shipments/{shipment_id}/status` (requiere Bearer token, cambia estado del despacho)
- `POST /api/v1/logistics/shipments/{shipment_id}/tracking` (registra punto GPS del despacho autorizado)
- `GET /api/v1/logistics/shipments/{shipment_id}/tracking` (historial GPS del despacho autorizado con filtros por rango)
- `GET /api/v1/inventory/items` (requiere Bearer token, listado paginado con filtros `farm_id`, `search`)
- `POST /api/v1/inventory/items` (requiere Bearer token, crea item de inventario)
- `GET /api/v1/inventory/items/{item_id}` (requiere Bearer token, detalle de item autorizado)
- `PATCH /api/v1/inventory/items/{item_id}` (requiere Bearer token, actualiza item autorizado)
- `GET /api/v1/inventory/movements` (requiere Bearer token, listado paginado con filtros `farm_id`, `item_id`, `movement_type`)
- `POST /api/v1/inventory/movements` (requiere Bearer token, crea movimiento y ajusta stock)
- `GET /api/v1/inventory/movements/{movement_id}` (requiere Bearer token, detalle de movimiento autorizado)
- `PATCH /api/v1/inventory/movements/{movement_id}` (requiere Bearer token, actualiza razón del movimiento)
- `GET /api/v1/marketplace/listings` (requiere Bearer token, listado paginado con filtros por finca/estado/producto/rango de publicación)
- `POST /api/v1/marketplace/listings` (requiere Bearer token, crea publicación de marketplace)
- `GET /api/v1/marketplace/listings/{listing_id}` (requiere Bearer token, detalle de publicación autorizada)
- `PATCH /api/v1/marketplace/listings/{listing_id}` (requiere Bearer token, actualiza publicación autorizada)
- `GET /api/v1/marketplace/offers` (requiere Bearer token, listado paginado de ofertas con filtros por publicación/estado/comprador)
- `POST /api/v1/marketplace/offers` (requiere Bearer token, crea oferta sobre publicación autorizada)
- `PATCH /api/v1/marketplace/offers/{offer_id}/status` (requiere Bearer token, cambia estado de oferta autorizada y registra auditoría)
- `GET /api/v1/reports/exports` (paginado con `limit`/`offset`, filtros por `farm_id`, `report_type`, `status`, rango `generated_from/generated_to`)
- `POST /api/v1/reports/exports` (crea registro de exportación de reporte)
- `GET /api/v1/reports/exports/{export_id}` (detalle de exportación autorizada)
- `PUT /api/v1/reports/exports/{export_id}` (actualiza metadatos de exportación autorizada)
- `PATCH /api/v1/reports/exports/{export_id}/status` (cambia estado de exportación autorizada)
- `PATCH /api/v1/reports/exports/{export_id}/sign` (firma exportación de reporte por agrónomo, registra hash y fecha de firma)
- `GET /api/v1/settings/farm` (listado paginado de configuraciones por finca/categoría/búsqueda)
- `POST /api/v1/settings/farm` (crea o actualiza configuración por `farm_id+category+setting_key`)
- `GET /api/v1/settings/farm/{setting_id}` (detalle de configuración autorizada)
- `PATCH /api/v1/settings/farm/{setting_id}` (actualiza `setting_value` con auditoría)
- `GET /api/v1/settings/farm/{setting_id}/history` (historial versionado de cambios de configuración por setting)
- `GET /api/v1/settings/templates` (catálogo de plantillas de configuración por tipo de cultivo)
- `POST /api/v1/settings/farm/apply-template` (aplica plantilla de cultivo a una finca autorizada)
- `GET /api/v1/ai/insights` (listado paginado de insights con filtros por finca/tipo/prioridad/confianza)
- `POST /api/v1/ai/insights` (crea insight de IA)
- `GET /api/v1/ai/insights/{insight_id}` (detalle de insight autorizado)
- `PATCH /api/v1/ai/insights/{insight_id}` (actualiza insight autorizado y registra auditoría)
- `PATCH /api/v1/ai/insights/{insight_id}/status` (transición de estado del insight con cierre de outcome y auditoría)
- `GET /api/v1/dashboard/kpis` (KPIs operativos/financieros por finca autorizada)
- `GET /api/v1/dashboard/kpis/compare` (comparativo de KPIs entre 2-5 fincas autorizadas)
- `POST /api/v1/dashboard/snapshots` (captura snapshot de KPIs)
- `GET /api/v1/dashboard/snapshots` (listado paginado de snapshots con filtros por finca/rango de captura)
- `GET /api/v1/dashboard/snapshots/{snapshot_id}` (detalle de snapshot autorizado)
- `GET /api/v1/dashboard/goals` (listado paginado de metas KPI por finca autorizada)
- `POST /api/v1/dashboard/goals` (crea meta KPI configurable por finca autorizada)
- `PATCH /api/v1/dashboard/goals/{goal_id}` (actualiza meta KPI configurable con auditoría)
- `GET /api/v1/dashboard/alerts` (alertas derivadas por brecha KPI vs meta activa)
- `GET /api/v1/gis/features` (listado paginado de elementos SIG con filtros por finca/lote/tipo/búsqueda)
- `POST /api/v1/gis/features` (crea elemento SIG)
- `GET /api/v1/gis/features/{feature_id}` (detalle de elemento SIG autorizado)
- `PATCH /api/v1/gis/features/{feature_id}` (actualiza elemento SIG autorizado y registra auditoría)
- `GET /api/v1/gis/features/{feature_id}/history` (historial versionado de cambios SIG por elemento autorizado)
- `GET /api/v1/nursery/` (listado paginado de lotes de vivero con filtros por finca/lote/estado/especie)
- `POST /api/v1/nursery/` (crea lote de vivero)
- `GET /api/v1/nursery/{batch_id}` (detalle de lote de vivero autorizado)
- `PATCH /api/v1/nursery/{batch_id}` (actualiza lote de vivero autorizado)
- `PATCH /api/v1/nursery/{batch_id}/status` (cambia estado de lote de vivero autorizado y registra auditoría)
- `GET /api/v1/phytosanitary/` (listado paginado de registros fitosanitarios con filtros por finca/lote/severidad/búsqueda)
- `POST /api/v1/phytosanitary/` (crea registro fitosanitario)
- `GET /api/v1/phytosanitary/{record_id}` (detalle de registro fitosanitario autorizado)
- `PATCH /api/v1/phytosanitary/{record_id}` (actualiza registro fitosanitario autorizado y registra auditoría)
- `GET /api/v1/quality/tests` (listado paginado de pruebas de calidad con filtros por finca/lote/estado/tipo)
- `POST /api/v1/quality/tests` (crea prueba de calidad)
- `GET /api/v1/quality/tests/{test_id}` (detalle de prueba de calidad autorizada)
- `PATCH /api/v1/quality/tests/{test_id}` (actualiza prueba de calidad autorizada y registra auditoría)
- `GET /api/v1/reports/overview.xlsx` (exportación Excel formal del resumen por finca)
- `GET /api/v1/reports/overview.pdf` (exportación PDF formal del resumen por finca)
- `GET /api/v1/reports/summary` (resumen agregado por tipo de reporte)
- `GET /api/v1/audit/logs` (paginado con `limit`/`offset`, respuesta `{total, items}`)
- `GET /api/v1/audit/exports` (paginado con `limit`/`offset`, respuesta `{total, items}`)
- `POST /api/v1/audit/exports` (genera solicitud de exportación de auditoría)
- `GET /api/v1/audit/exports/{export_id}` (detalle de exportación propia de auditoría)
- `PATCH /api/v1/audit/exports/{export_id}` (actualiza metadatos de exportación propia y registra auditoría)
- `PATCH /api/v1/audit/exports/{export_id}/status` (actualiza estado de exportación de auditoría con control de transición)

## Configurar MySQL local (sin Docker)
1. Instalar MySQL 8.0 en tu máquina.
2. Crear base y usuario:
```sql
CREATE DATABASE cultivos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'cultivos'@'localhost' IDENTIFIED BY 'cultivos123';
GRANT ALL PRIVILEGES ON cultivos.* TO 'cultivos'@'localhost';
FLUSH PRIVILEGES;
```
3. Copiar variables de entorno:
```bash
cp .env.example .env
```

## Migración inicial
Aplicar, en orden:
- `db/migrations/001_init.sql`
- `db/migrations/002_plots.sql`
- `db/migrations/003_crop_cycles.sql`
- `db/migrations/004_tasks.sql`
- `db/migrations/005_inputs.sql`
- `db/migrations/006_harvests.sql`
- `db/migrations/007_monitoring.sql`
- `db/migrations/008_weather.sql`
- `db/migrations/009_irrigation.sql`
- `db/migrations/010_rotation.sql`
- `db/migrations/011_workers.sql`
- `db/migrations/012_machines.sql`
- `db/migrations/013_inventory.sql`

## Estructura de carpetas (base)
- `app/api/` rutas HTTP
- `app/core/` configuración y seguridad transversal
- `app/db/` conexión/sesiones/base ORM
- `app/models/` entidades ORM
- `app/schemas/` esquemas request/response
- `app/services/` lógica de negocio
- `app/repositories/` acceso a datos
- `app/tests/` pruebas
- `db/migrations/` migraciones SQL
- `docs/` documentación técnica y funcional


## Variables de entorno adicionales
- `REFRESH_TOKEN_EXPIRE_MINUTES`: duración en minutos del refresh token.
- `APP_VERSION`: versión del servicio expuesta en health/OpenAPI.
- `API_V1_PREFIX`: prefijo lógico de API v1 (documentación y configuración).
- `CORS_ALLOW_ORIGINS`: lista CSV de orígenes permitidos (o `*`).


## Contrato de error estándar
Todas las respuestas de error HTTP ahora incluyen:
- Header `x-request-id`
- Cuerpo JSON con formato:
```json
{
  "request_id": "<uuid>",
  "error": {
    "code": "http_403 | validation_error | ...",
    "message": "mensaje legible",
    "details": {}
  }
}
```
Esto facilita trazabilidad y correlación entre cliente, logs y auditoría.
