# Cultivos API (Inicio)

Base inicial del sistema integral de cultivos.

## Stack elegido
- **Backend:** FastAPI (Python 3.11)
- **ORM:** SQLAlchemy 2.x
- **Base de datos:** MySQL 8.0
- **Autenticación:** JWT (estructura base)
- **Infra local:** MySQL instalado localmente (sin Docker)

## Módulos iniciales implementados (estructura)
- M1: Autenticación/Usuarios (base)
- M2: Fincas (base)
- Auditoría (base)

## Ejecutar local (cuando instales dependencias)
```bash
uv run uvicorn app.main:app --reload
```

## Endpoints iniciales funcionales
- `GET /api/v1/health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/farms/` (requiere Bearer token, lista fincas del usuario)
- `POST /api/v1/farms/` (requiere Bearer token, crea finca y asigna rol dueño)
- `GET /api/v1/plots/` (requiere Bearer token, lista lotes de fincas asignadas)
- `POST /api/v1/plots/` (requiere Bearer token, valida acceso a finca)
- `GET /api/v1/crop-cycles/` (requiere Bearer token, lista ciclos por fincas del usuario)
- `POST /api/v1/crop-cycles/` (requiere Bearer token, crea ciclo en lote autorizado)
- `GET /api/v1/tasks/` (requiere Bearer token, lista labores por fincas del usuario)
- `POST /api/v1/tasks/` (requiere Bearer token, crea labor en lote autorizado)
- `PATCH /api/v1/tasks/{task_id}/status` (requiere Bearer token, cambia estado de labor)
- `GET /api/v1/inputs/products` (requiere Bearer token, lista catálogo de insumos)
- `POST /api/v1/inputs/products` (requiere Bearer token, crea insumo)
- `GET /api/v1/inputs/applications` (requiere Bearer token, lista aplicaciones por fincas del usuario)
- `POST /api/v1/inputs/applications` (requiere Bearer token, registra aplicación de insumo)
- `GET /api/v1/harvests/` (requiere Bearer token, lista cosechas por fincas del usuario)
- `POST /api/v1/harvests/` (requiere Bearer token, registra cosecha en lote autorizado)
- `GET /api/v1/monitoring/visits` (requiere Bearer token, lista monitoreos por fincas del usuario)
- `POST /api/v1/monitoring/visits` (requiere Bearer token, registra visita de monitoreo)
- `GET /api/v1/weather/observations` (requiere Bearer token, lista observaciones climáticas)
- `POST /api/v1/weather/observations` (requiere Bearer token, registra observación climática)
- `GET /api/v1/irrigation/events` y `POST /api/v1/irrigation/events` (M10 riego)
- `GET /api/v1/rotation/plans` y `POST /api/v1/rotation/plans` (M11 rotación)
- `GET /api/v1/workers/` y `POST /api/v1/workers/` (M12 recurso humano)
- `GET /api/v1/machines/` y `POST /api/v1/machines/` (M13 maquinaria)
- `GET /api/v1/inventory/items` / `POST /api/v1/inventory/items` (M14 inventario)
- `GET /api/v1/inventory/movements` / `POST /api/v1/inventory/movements` (M14 inventario)

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
