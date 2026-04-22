from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pymysql
from pymysql.connections import Connection


@dataclass(frozen=True)
class MigrationFile:
    version: str
    filename: str
    path: Path


def discover_migrations(migrations_dir: str | Path) -> list[MigrationFile]:
    root = Path(migrations_dir)
    if not root.exists():
        raise FileNotFoundError(f"No existe el directorio de migraciones: {root}")

    discovered: list[MigrationFile] = []
    for file in root.glob("*.sql"):
        version = parse_version(file.name)
        discovered.append(MigrationFile(version=version, filename=file.name, path=file))
    return sorted(discovered, key=lambda item: item.version)


def parse_version(filename: str) -> str:
    prefix = filename.split("_", 1)[0]
    if not prefix or not prefix.isdigit():
        raise ValueError(f"Nombre de migración inválido: {filename}")
    return prefix


def ensure_schema_migrations_table(connection: Connection) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(20) PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
    connection.commit()


def load_applied_versions(connection: Connection) -> set[str]:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version FROM schema_migrations")
        rows = cursor.fetchall()
    return {str(row[0]) for row in rows}


def apply_migrations(connection: Connection, migrations: Iterable[MigrationFile]) -> list[MigrationFile]:
    applied = load_applied_versions(connection)
    executed: list[MigrationFile] = []

    for migration in migrations:
        if migration.version in applied:
            continue
        sql = migration.path.read_text(encoding="utf-8")
        with connection.cursor() as cursor:
            for statement in split_sql_statements(sql):
                cursor.execute(statement)
            cursor.execute(
                "INSERT INTO schema_migrations (version, filename) VALUES (%s, %s)",
                (migration.version, migration.filename),
            )
        connection.commit()
        executed.append(migration)
    return executed


def split_sql_statements(sql: str) -> list[str]:
    statements = [chunk.strip() for chunk in sql.split(";")]
    return [statement for statement in statements if statement]


def open_mysql_connection(*, host: str, port: int, user: str, password: str, database: str) -> Connection:
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
        autocommit=False,
    )
