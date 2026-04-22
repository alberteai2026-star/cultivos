from pathlib import Path

from app.core.config import settings
from app.db.migration_runner import (
    apply_migrations,
    discover_migrations,
    ensure_schema_migrations_table,
    open_mysql_connection,
)


def main() -> int:
    migrations_dir = Path(__file__).resolve().parents[1] / "db" / "migrations"
    migrations = discover_migrations(migrations_dir)
    if not migrations:
        print("No hay migraciones encontradas.")
        return 0

    connection = open_mysql_connection(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=settings.mysql_db,
    )
    try:
        ensure_schema_migrations_table(connection)
        executed = apply_migrations(connection, migrations)
    finally:
        connection.close()

    if not executed:
        print("Base de datos al día. No hay migraciones pendientes.")
        return 0

    print(f"Migraciones aplicadas: {len(executed)}")
    for migration in executed:
        print(f" - {migration.filename}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
