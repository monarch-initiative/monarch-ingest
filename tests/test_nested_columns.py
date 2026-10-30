"""Nested (STRUCT / MAP) columns, e.g. Biolink `sources`, are written as JSON
text in exports whose targets can't hold records: Neo4j CSV and SQLite."""

import json
import sqlite3

import duckdb
import pytest

from monarch_ingest.cli_utils import (
    get_neo4j_column_from_db,
    is_nested_column_type,
    sqlite_select_list,
)

SOURCES_TYPE = (
    "STRUCT(resource_id VARCHAR, resource_role VARCHAR, source_record_urls VARCHAR[])[]"
)
SOURCES = [
    {
        "resource_id": "infores:fda-dailymed",
        "resource_role": "primary_knowledge_source",
        # ';' in a URL must not split the value in Neo4j's string[] handling
        "source_record_urls": ["https://example.org/lookup;setid=1"],
    }
]


@pytest.fixture
def con():
    con = duckdb.connect()
    con.execute(f"CREATE TABLE edges (id VARCHAR, publications VARCHAR[], sources {SOURCES_TYPE})")
    con.execute("INSERT INTO edges VALUES ('e1', ['PMID:1', 'PMID:2'], ?)", [SOURCES])
    yield con
    con.close()


@pytest.mark.parametrize(
    "col_type, nested",
    [
        (SOURCES_TYPE, True),
        ("STRUCT(a VARCHAR)", True),
        ("MAP(VARCHAR, VARCHAR)", True),
        ("VARCHAR[]", False),
        ("VARCHAR", False),
        ("BIGINT", False),
    ],
)
def test_is_nested_column_type(col_type, nested):
    assert is_nested_column_type(col_type) is nested


def test_neo4j_writes_nested_column_as_one_json_string(con):
    column_types = dict(con.execute("SELECT column_name, column_type FROM (DESCRIBE edges)").fetchall())
    select = get_neo4j_column_from_db("sources", column_types)
    assert select.endswith('"sources:string"')
    value = con.execute(f"SELECT {select} FROM edges").fetchone()[0]
    assert json.loads(value) == SOURCES
    # plain lists keep the string[] path
    assert "array_to_string" in get_neo4j_column_from_db("publications", column_types)


def test_sqlite_copy_writes_nested_column_as_json_text(con, tmp_path):
    sqlite_path = tmp_path / "test.db"
    sqlite3.connect(sqlite_path).close()
    con.execute("INSTALL sqlite")
    con.execute("LOAD sqlite")
    con.execute(f"ATTACH '{sqlite_path}' AS sqlite_db (TYPE SQLITE, READ_ONLY FALSE)")
    con.execute(f"CREATE TABLE sqlite_db.edges AS SELECT {sqlite_select_list(con, 'edges')} FROM edges")
    con.execute("DETACH sqlite_db")

    row = sqlite3.connect(sqlite_path).execute(
        "SELECT id, json_extract(sources, '$[0].resource_id') FROM edges"
    ).fetchone()
    assert row == ("e1", "infores:fda-dailymed")


@pytest.mark.parametrize(
    "col_type, header",
    [
        ("BIGINT[]", '"locs:long[]"'),
        ("DOUBLE[]", '"locs:float[]"'),
        ("BOOLEAN[]", '"locs:boolean[]"'),
        ("BIGINT", '"locs:long"'),
    ],
)
def test_neo4j_typed_arrays_keep_element_type(col_type, header):
    """A BIGINT[] column (e.g. MeDIC's object_location_in_text) is a long[]
    property, joined on Neo4j's ';' array delimiter — not `:long`, which
    neo4j-admin import rejects for a value like "[1756, 1767]"."""
    select = get_neo4j_column_from_db("locs", {"locs": col_type})
    assert select.endswith(header)
    if col_type.endswith("[]"):
        assert select.startswith("array_to_string(locs, ';')")
