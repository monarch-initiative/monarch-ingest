"""Annotation-IC tables for the Monarch API's phenotype search groups (monarch-app #1475)."""

import math

import duckdb
import pytest

from monarch_ingest.cli_utils import SEARCH_ANNOTATION_IC_CORPORA, compute_search_annotation_ic_tables

G2P = "biolink:GeneToPhenotypicFeatureAssociation"


@pytest.fixture
def kg(tmp_path):
    """HP: HP:2 < HP:1. WBPhenotype: WBPhenotype:2 < WBPhenotype:1. MP: MP:1.
    Human genes HGNC:1 -> HP:2, HGNC:2 -> HP:1, HGNC:3 -> HP:2 (negated, excluded).
    Rat gene RGD:1 -> MP:1. Worm genes WB:1, WB:2 -> WBPhenotype:2."""
    path = tmp_path / "monarch-kg.duckdb"
    con = duckdb.connect(str(path))
    con.execute("CREATE TABLE closure(subject_id VARCHAR, predicate_id VARCHAR, object_id VARCHAR)")
    con.executemany(
        "INSERT INTO closure VALUES (?, 'rdfs:subClassOf', ?)",
        [
            ("HP:1", "HP:1"),
            ("HP:2", "HP:2"),
            ("HP:2", "HP:1"),
            ("MP:1", "MP:1"),
            ("WBPhenotype:1", "WBPhenotype:1"),
            ("WBPhenotype:2", "WBPhenotype:2"),
            ("WBPhenotype:2", "WBPhenotype:1"),
        ],
    )
    con.execute(
        "CREATE TABLE edges(subject VARCHAR, predicate VARCHAR, object VARCHAR, category VARCHAR, negated BOOLEAN)"
    )
    con.executemany(
        f"INSERT INTO edges VALUES (?, 'biolink:has_phenotype', ?, '{G2P}', ?)",
        [
            ("HGNC:1", "HP:2", False),
            ("HGNC:2", "HP:1", False),
            ("HGNC:3", "HP:2", True),
            ("RGD:1", "MP:1", False),
            ("WB:1", "WBPhenotype:2", False),
            ("WB:2", "WBPhenotype:2", False),
        ],
    )
    # the corpus table pheno_comparisons' compute_information_content_tables writes first
    con.execute(
        """CREATE TABLE pheno_comparison_corpora (corpus VARCHAR, ic_table VARCHAR, description VARCHAR,
        categories VARCHAR[], subject_prefixes VARCHAR[], object_prefixes VARCHAR[], entity_count BIGINT,
        association_count BIGINT, term_count BIGINT, koza_version VARCHAR, computed_at VARCHAR)"""
    )
    con.execute(
        """INSERT INTO pheno_comparison_corpora VALUES ('hp', 'information_content_mondo_hp', 'diseases',
        ['x'], ['MONDO'], ['HP'], 1, 1, 1, 'v', 't')"""
    )
    con.close()
    return path


def test_writes_one_table_per_search_group_and_registers_it(kg):
    rows = compute_search_annotation_ic_tables(kg)
    assert [r["ic_table"] for r in rows] == [c[1] for c in SEARCH_ANNOTATION_IC_CORPORA]
    con = duckdb.connect(str(kg), read_only=True)
    corpora = dict(con.execute("SELECT ic_table, subject_prefixes FROM pheno_comparison_corpora").fetchall())
    # the existing Exomiser corpus row is kept; the three search corpora are added
    assert corpora == {
        "information_content_mondo_hp": ["MONDO"],
        "information_content_hgnc_hp": ["HGNC"],
        "information_content_rgd_mp": ["RGD"],
        "information_content_wb_wbphenotype": ["WB"],
    }
    hgnc = dict(con.execute("SELECT term, ic FROM information_content_hgnc_hp").fetchall())
    # N = 2 human genes (HGNC:3's only edge is negated). HP:1 reaches both, HP:2 only HGNC:1.
    assert hgnc == {"HP:1": pytest.approx(0.0), "HP:2": pytest.approx(math.log2(2))}
    worm = dict(con.execute("SELECT term, ic FROM information_content_wb_wbphenotype").fetchall())
    assert worm["WBPhenotype:2"] == pytest.approx(0.0)


def test_rerunning_replaces_rather_than_duplicates_rows(kg):
    compute_search_annotation_ic_tables(kg)
    compute_search_annotation_ic_tables(kg)
    con = duckdb.connect(str(kg), read_only=True)
    assert con.execute("SELECT count(*) FROM pheno_comparison_corpora").fetchone()[0] == 4
