# Estado de Implementación (snapshot)

Fecha de corte: **2026-04-22**.

## 1) Resumen ejecutivo

- Fases completas: **0/7**
- Módulos completos: **21/32**
- Sprints completos: **3/36**
- Submódulos completos: **15/111**

## 2) Módulos pendientes

1. M22 — Reportes y analítica
2. M23 — IA insights
3. M24 — Auditoría
4. M25 — Ajustes
5. M26 — Dashboard
6. M27 — Cartografía SIG
7. M28 — IoT (parcial: S1 completado)
8. M29 — Seguimiento vehicular/GPS (parcial: tracking por despacho)
9. M30 — Seguimiento empleados en campo (parcial: tracking por trabajador)
10. M31 — Vigilancia y seguridad perimetral (parcial: incidentes)
11. M32 — Contabilidad agrícola NIIF (parcial: diario y balance)

## 3) IoT (M28) detalle

- ✅ M28.S1 Registro de sensores
- ⏳ M28.S2 Lecturas en tiempo real (actual: stream WebSocket básico `WS /api/v1/iot/readings/stream` + polling `GET /api/v1/iot/readings/latest`)
- ✅ M28.S3 Reglas de automatización (básico: `GET/POST /api/v1/iot/rules` + `GET /api/v1/iot/alerts`)
- ✅ M28.S4 Control de electroválvulas (básico: `GET/POST /api/v1/iot/valves/commands`)

Capacidades actuales adicionales de API IoT:
- `GET /api/v1/iot/readings` con paginación (`limit`, `offset`)
- `GET /api/v1/iot/readings/latest` para consumo por polling
- `WS /api/v1/iot/readings/stream` con token por `Authorization: Bearer ...` (o `?token=...`)
- Validación básica en stream (`limit`, `device_id`) y cierre por política ante token/acceso inválido

## 4) Qué falta para declarar “producción”

Pendiente completar el DoD operativo global:

- Validación de migraciones en staging.
- Pruebas unitarias/integración/E2E/UAT aprobadas.
- Verificación integral de RBAC + auditoría.
- Observabilidad activa (logs, métricas, alertas).
- Manual técnico y operativo actualizado.

## 5) Reportes (M22) avance parcial

- `GET /api/v1/reports/overview` resumen consolidado por finca.
- `GET /api/v1/reports/overview.csv` exportación CSV básica del resumen.
- `GET /api/v1/reports/overview.json` exportación JSON descargable del resumen.
- `GET /api/v1/reports/overview.xlsx` exportación Excel formal del resumen.
- `GET /api/v1/reports/overview.pdf` exportación PDF formal del resumen.
- `GET /api/v1/reports/templates` listado paginado de plantillas por finca/tipo/estado.
- `POST /api/v1/reports/templates` creación de plantilla de reporte reutilizable.
- `GET /api/v1/reports/templates/{template_id}` detalle de plantilla autorizada.
- `PATCH /api/v1/reports/templates/{template_id}` edición de plantilla (nombre, formato, filtros y estado activo).
- `POST /api/v1/reports/templates/{template_id}/generate` generación de exportación a partir de plantilla activa.
- `GET /api/v1/reports/exports` con filtros (`farm_id`, `report_type`, `status`, `generated_from`, `generated_to`) y paginación (`limit`, `offset`).
- `GET /api/v1/reports/exports/{export_id}` detalle de exportación con control de acceso por finca.
- `PUT /api/v1/reports/exports/{export_id}` actualización de metadatos de exportación.
- `PATCH /api/v1/reports/exports/{export_id}/status` cambio de estado con traza de auditoría.
- `PATCH /api/v1/reports/exports/{export_id}/sign` firma agronómica (nombre, hash, fecha) con auditoría (`reports:sign_export`).
- Pendiente: plantillas productivas/financieras completas y maquetación avanzada de reportes formales.

## 6) Próximo foco recomendado (orden)

1. M22 Reportes (PDF/Excel + firma agrónomo)
2. M23 IA (recomendaciones y alertas)
3. M24 Auditoría forense
4. M25 Ajustes e integraciones externas
5. M26 Dashboard consolidado

## 7) Auditoría (M24) avance parcial

- `GET /api/v1/audit/logs` listado con filtros (`farm_id`, `module`, `action`) y paginación.
- `GET /api/v1/audit/summary` resumen forense agregado por (`module`, `action`) con filtros y rango temporal.
- `POST /api/v1/audit/exports` creación de exportación con firma hash de filtros.
- `GET /api/v1/audit/exports` listado de exportaciones propias.
- `GET /api/v1/audit/exports/{export_id}` detalle de exportación propia con control de acceso por usuario/finca.
- `GET /api/v1/audit/exports/{export_id}/verify-signature` verificación de integridad de firma contra filtros persistidos.
- `PATCH /api/v1/audit/exports/{export_id}` actualización de metadatos (`format`, `file_url`, `signature`) con traza en `audit_logs`.
- `PATCH /api/v1/audit/exports/{export_id}/status` transición de estado (`solicitado/procesando/completado/fallido`) con auditoría (`audit:update_export_status`).
- Pendiente: orquestación asíncrona masiva, conservación WORM y validación criptográfica avanzada.

## 8) Ajustes (M25) avance parcial

- `GET /api/v1/settings/farm` listado paginado de configuraciones con filtros (`farm_id`, `category`, `search`).
- `POST /api/v1/settings/farm` alta/actualización idempotente por llave funcional (`farm_id`, `category`, `setting_key`).
- `GET /api/v1/settings/farm/{setting_id}` detalle con control de acceso por finca.
- `PATCH /api/v1/settings/farm/{setting_id}` actualización de valor con evento de auditoría (`settings:update_value`).
- `GET /api/v1/settings/farm/{setting_id}/history` historial versionado de cambios por setting.
- `GET /api/v1/settings/templates` catálogo de plantillas por tipo de cultivo.
- `POST /api/v1/settings/farm/apply-template` aplicación masiva de plantilla a finca autorizada.
- Pendiente: integraciones externas avanzadas; ya habilitado versionado básico e instalación por plantillas de cultivo.

## 9) IA insights (M23) avance parcial

- `GET /api/v1/ai/insights` listado paginado con filtros (`farm_id`, `insight_type`, `priority`, `confidence_min/max`).
- `POST /api/v1/ai/insights` creación de insight con control RBAC por finca.
- `GET /api/v1/ai/insights/{insight_id}` detalle de insight autorizado.
- `PATCH /api/v1/ai/insights/{insight_id}` actualización de insight con traza en auditoría (`ai:update_insight`).
- `PATCH /api/v1/ai/insights/{insight_id}/status` transición de estado (`nuevo → en_revision → aplicado → validado/descartado`) con auditoría (`ai:update_insight_status`).
- `GET /api/v1/ai/insights/recommendations` backlog priorizado de recomendaciones accionables con filtros de confianza.
- `GET /api/v1/ai/insights/summary` resumen agregado por (`insight_type`, `status`, `priority`) para seguimiento operativo.
- `GET /api/v1/ai/insights/yield-forecast` proyección por lote usando promedio histórico de cosecha + predicción IA más reciente.
- `GET /api/v1/ai/insights/predictive-alerts` alertas predictivas activas (`risk_alert`) con umbral configurable de confianza.
- Pendiente: explainability avanzada por variable/fuente y validación online de drift/modelo.

## 10) Dashboard (M26) avance parcial

- `GET /api/v1/dashboard/kpis` KPIs por finca (ciclos activos, tareas pendientes, stock crítico, ingresos/costos y neto).
- `GET /api/v1/dashboard/kpis/compare` comparativo multi-finca de KPIs autorizados.
- `POST /api/v1/dashboard/snapshots` captura manual de KPIs para trazabilidad histórica.
- `GET /api/v1/dashboard/snapshots` listado paginado con filtros (`farm_id`, `captured_from`, `captured_to`).
- `GET /api/v1/dashboard/snapshots/{snapshot_id}` detalle de snapshot autorizado.
- `GET /api/v1/dashboard/goals` listado paginado de metas KPI con filtros (`farm_id`, `status`, `kpi_key`).
- `POST /api/v1/dashboard/goals` creación de meta KPI por finca autorizada.
- `PATCH /api/v1/dashboard/goals/{goal_id}` actualización de meta KPI (`target_value`, `period_label`, `status`) con auditoría.
- `GET /api/v1/dashboard/alerts` alertas derivadas de metas activas vs KPI actual (`ok`, `warning`, `critical`).
- Pendiente: widgets comparativos multi-finca avanzados y alertas visuales en tiempo real para frontend.

## 11) Cartografía SIG (M27) avance parcial

- `GET /api/v1/gis/features` listado paginado de features con filtros (`farm_id`, `plot_id`, `feature_type`, `search`).
- `POST /api/v1/gis/features` creación de feature con control RBAC por finca.
- `GET /api/v1/gis/features/{feature_id}` detalle de feature autorizado.
- `PATCH /api/v1/gis/features/{feature_id}` actualización de feature con auditoría (`gis:update_feature`).
- `GET /api/v1/gis/features/{feature_id}/history` historial versionado por feature SIG (snapshot por versión).
- Pendiente: validación topológica avanzada y capas raster/vectoriales externas.

## 12) Vivero (M16) avance parcial

- `GET /api/v1/nursery/` listado paginado de lotes con filtros (`farm_id`, `plot_id`, `status`, `search`).
- `POST /api/v1/nursery/` creación de lote de vivero con RBAC por finca.
- `GET /api/v1/nursery/{batch_id}` detalle de lote autorizado.
- `PATCH /api/v1/nursery/{batch_id}` actualización de datos de lote.
- `PATCH /api/v1/nursery/{batch_id}/status` transición de estado con traza de auditoría (`nursery:update_status`).
- Pendiente: trazabilidad por bandeja/lote hijo, supervivencia por etapa y alertas fitosanitarias de vivero.

## 13) Fitosanitario (M17) avance parcial

- `GET /api/v1/phytosanitary/` listado paginado con filtros (`farm_id`, `plot_id`, `severity`, `search`).
- `POST /api/v1/phytosanitary/` creación de registro fitosanitario con RBAC por finca.
- `GET /api/v1/phytosanitary/{record_id}` detalle de registro autorizado.
- `PATCH /api/v1/phytosanitary/{record_id}` actualización de registro con auditoría (`phytosanitary:update`).
- Pendiente: alertas tempranas automáticas, historial por plaga/enfermedad y protocolos de tratamiento recomendados.

## 14) Calidad (M15) avance parcial

- `GET /api/v1/quality/tests` listado paginado con filtros (`farm_id`, `plot_id`, `status`, `test_type`).
- `POST /api/v1/quality/tests` creación de prueba de calidad con RBAC por finca.
- `GET /api/v1/quality/tests/{test_id}` detalle de prueba autorizada.
- `PATCH /api/v1/quality/tests/{test_id}` actualización de prueba con auditoría (`quality:update_test`).
- Pendiente: reglas de aceptación por cultivo/mercado, trazabilidad de laboratorio y certificados automáticos por lote.


## 15) Marketplace (M21) avance parcial

- `GET /api/v1/marketplace/listings` listado paginado con filtros (`farm_id`, `status`, `product_search`, `published_from`, `published_to`).
- `POST /api/v1/marketplace/listings` creación de publicación con control RBAC por finca.
- `GET /api/v1/marketplace/listings/{listing_id}` detalle de publicación autorizada.
- `PATCH /api/v1/marketplace/listings/{listing_id}` actualización de publicación con auditoría (`marketplace:update_listing`).
- `GET /api/v1/marketplace/offers` listado paginado de ofertas con filtros (`listing_id`, `status`, `buyer_search`).
- `POST /api/v1/marketplace/offers` creación de oferta sobre publicación autorizada.
- `PATCH /api/v1/marketplace/offers/{offer_id}/status` transición de estado con auditoría (`marketplace:update_offer_status`).
- Pendiente: workflow de negociación multi-actor, expiración automática y chat comprador-vendedor.


## 16) Logística/GPS (M29) avance parcial

- `POST /api/v1/logistics/shipments/{shipment_id}/tracking` registra punto GPS en despacho autorizado.
- `GET /api/v1/logistics/shipments/{shipment_id}/tracking` historial paginado de puntos GPS con filtros (`recorded_from`, `recorded_to`).
- Pendiente: telemetría en tiempo real, geocercas y alertas de desvío de ruta.


## 17) Seguimiento de empleados (M30) avance parcial

- `POST /api/v1/workers/{worker_id}/tracking` registra ubicación de trabajador autorizado.
- `GET /api/v1/workers/{worker_id}/tracking` historial paginado de ubicaciones con filtros (`recorded_from`, `recorded_to`).
- Pendiente: geocercas por cuadrilla, alertas SOS y validación de jornada en tiempo real.


## 18) Seguridad perimetral (M31) avance parcial

- `GET /api/v1/security/incidents` listado paginado de incidentes con filtros (`farm_id`, `status`, `severity`).
- `POST /api/v1/security/incidents` creación de incidente con control RBAC por finca.
- `GET /api/v1/security/incidents/{incident_id}` detalle de incidente autorizado.
- `PATCH /api/v1/security/incidents/{incident_id}/status` cierre/actualización con traza de auditoría.
- Pendiente: videoanalítica, integración CCTV y detección inteligente en tiempo real.


## 19) Contabilidad NIIF (M32) avance parcial

- `POST /api/v1/finance/journal-entries` registra asientos contables balanceados (debe = haber).
- `GET /api/v1/finance/journal-entries` listado paginado de asientos por finca autorizada.
- `GET /api/v1/finance/trial-balance` balance de comprobación por cuenta contable.
- Pendiente: catálogo NIIF completo, cierre contable y estados financieros formales.

## 20) Salud operativa (Health/Readiness) — actualización 2026-04-22

- `GET /api/v1/health` endpoint canónico de salud del servicio.
- `GET /api/v1/health/ready` readiness probe con validación de base de datos (`200` cuando DB está disponible, `503` cuando no lo está).
- `GET /api/v1/health/health` alias legado marcado como deprecado para compatibilidad retroactiva.
