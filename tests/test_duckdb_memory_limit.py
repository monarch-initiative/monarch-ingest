import duckdb
import pytest

from monarch_ingest.cli_utils import connect_duckdb


@pytest.mark.parametrize("read_only", [False, True])
def test_connect_duckdb_honors_memory_limit(tmp_path, monkeypatch, read_only):
    path = tmp_path / "kg.duckdb"
    duckdb.connect(str(path)).close()
    monkeypatch.setenv("DUCKDB_MEMORY_LIMIT", "512MB")
    con = connect_duckdb(path, read_only=read_only)
    limit = con.execute("SELECT current_setting('memory_limit')").fetchone()[0]
    con.close()
    assert limit.startswith(("512", "488")), limit


def test_connect_duckdb_keeps_default_without_env(tmp_path, monkeypatch):
    monkeypatch.delenv("DUCKDB_MEMORY_LIMIT", raising=False)
    default = duckdb.connect().execute("SELECT current_setting('memory_limit')").fetchone()[0]
    con = connect_duckdb(tmp_path / "kg.duckdb")
    assert con.execute("SELECT current_setting('memory_limit')").fetchone()[0] == default
    con.close()
