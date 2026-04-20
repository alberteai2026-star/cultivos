# Estado de Implementación (snapshot)

Fecha de corte: **2026-04-20**.

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
8. M29 — Seguimiento vehicular/GPS
9. M30 — Seguimiento empleados en campo
10. M31 — Vigilancia y seguridad perimetral
11. M32 — Contabilidad agrícola NIIF

## 3) IoT (M28) detalle

- ✅ M28.S1 Registro de sensores
- ⏳ M28.S2 Lecturas en tiempo real (actual: stream WebSocket básico `WS /api/v1/iot/readings/stream` + polling `GET /api/v1/iot/readings/latest`)
- ⏳ M28.S3 Reglas de automatización
- ⏳ M28.S4 Control de electroválvulas

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
- Pendiente: plantillas productivas/financieras completas, export Excel/PDF formal y firma agrónomo.

## 6) Próximo foco recomendado (orden)

1. M22 Reportes (PDF/Excel + firma agrónomo)
2. M23 IA (recomendaciones y alertas)
3. M24 Auditoría forense
4. M25 Ajustes e integraciones externas
5. M26 Dashboard consolidado
