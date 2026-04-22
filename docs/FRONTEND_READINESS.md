# Frontend Readiness Checklist (estado actual)

Fecha de actualización: **2026-04-22**.

## 1) Ya disponible para arrancar frontend

- Autenticación base con JWT (`/api/v1/auth/login`) y dependencia de usuario actual.
- Convención transversal de control de acceso por finca (RBAC) en servicios.
- Múltiples módulos con endpoints de listado + detalle + actualización (reports, audit, settings, ai, dashboard, gis).
- Contratos Pydantic estables en `app/schemas/*` para tipado en cliente.

## 2) Faltantes recomendados antes de UI productiva

### A. Contrato y DX API

1. **Normalizar formato de listas** en todos los módulos a `{ total, items }`.
   - Hoy algunos endpoints ya están normalizados, otros aún no.
2. **Errores de validación homogéneos** (catálogo de códigos de error por dominio).
3. **Versionado de API explícito por breaking changes** (documentar estrategia `v1`→`v2`).
4. **Documentación OpenAPI curada**:
   - ejemplos de request/response,
   - enums documentados,
   - flujos de error más comunes.

### B. Autenticación / sesión para SPA

1. Endpoint de **refresh token** (si se requiere sesión prolongada).
2. Política de expiración/renovación de token documentada para frontend.
3. Estrategia de manejo de `401/403` estandarizada (incluyendo reintento y logout).

### C. UX de datos y performance

1. Filtros/sort/paginación consistentes en módulos restantes.
2. Endpoints agregados para pantallas densas (dashboard principal, resumenes cross-módulo).
3. Definir límites por endpoint (`limit` máximos) y recomendaciones de consumo.

### D. Operación y confiabilidad

1. Seeds/datos de demo para acelerar QA visual del frontend.
2. Ambiente `staging` estable con CORS y auth configurados.
3. Observabilidad mínima para front:
   - correlation/request-id en respuestas de error,
   - logging de fallos por endpoint.

## 3) Orden sugerido para arrancar frontend mañana mismo

1. **Auth + layout base + guardas de ruta**.
2. **Farms context** (selección de finca activa).
3. Módulos ya más maduros:
   - Reports,
   - Settings,
   - AI insights,
   - Dashboard snapshots,
   - GIS features.
4. Tablas con búsqueda/filtros y estados de carga/error reutilizables.
5. Último tramo: módulos con contrato aún parcial.

## 4) Checklist técnico mínimo (Go / No-Go)

- [ ] Ambiente backend compartido y estable (staging o local dockerizado).
- [ ] `.env` frontend con `API_BASE_URL` y estrategia de auth definida.
- [ ] Convención de errores acordada (`detail`, código, request_id).
- [ ] Convención de listas acordada (`total/items`) en endpoints usados por la primera release UI.
- [ ] Mockups/alcance de primeras pantallas cerrados.
