from pathlib import Path

import pytest

from app.db.migration_runner import discover_migrations, parse_version, split_sql_statements


def test_parse_version_accepts_numeric_prefix():
    assert parse_version("001_init.sql") == "001"
    assert parse_version("041_report_templates.sql") == "041"


def test_parse_version_rejects_invalid_filename():
    with pytest.raises(ValueError):
        parse_version("init.sql")


def test_split_sql_statements_filters_empty_chunks():
    sql = """
    CREATE TABLE test_a (id INT);

    CREATE TABLE test_b (id INT);
    """
    statements = split_sql_statements(sql)
    assert len(statements) == 2
    assert "CREATE TABLE test_a" in statements[0]
    assert "CREATE TABLE test_b" in statements[1]


def test_discover_migrations_sorts_by_version(tmp_path: Path):
    (tmp_path / "010_rotation.sql").write_text("SELECT 1;", encoding="utf-8")
    (tmp_path / "002_plots.sql").write_text("SELECT 2;", encoding="utf-8")
    (tmp_path / "001_init.sql").write_text("SELECT 3;", encoding="utf-8")

    migrations = discover_migrations(tmp_path)
    assert [item.version for item in migrations] == ["001", "002", "010"]
