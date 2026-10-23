"""Annotation IC for the Monarch API's phenotype search groups (monarch-app #1475)."""

import math

import duckdb
import pytest

from monarch_ingest.cli_utils import SEARCH_ANNOTATION_IC_CORPORA, compute_search_annotation_ic

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
    # what pheno_comparisons' compute_information_content_tables writes first
    con.execute("""CREATE TABLE pheno_comparison_corpora (corpus VARCHAR, description VARCHAR,
        categories VARCHAR[], subject_prefixes VARCHAR[], object_prefixes VARCHAR[], entity_count BIGINT,
        association_count BIGINT, term_count BIGINT, koza_version VARCHAR, computed_at VARCHAR)""")
    con.execute("""INSERT INTO pheno_comparison_corpora VALUES ('mondo_hp', 'diseases',
        ['x'], ['MONDO'], ['HP'], 1, 1, 1, 'v', 't')""")
    con.execute("CREATE TABLE annotation_information_content (corpus VARCHAR, term VARCHAR, ic DOUBLE)")
    con.execute("INSERT INTO annotation_information_content VALUES ('mondo_hp', 'HP:1', 5.0)")
    con.close()
    return path


def _ic(con, corpus):
    return dict(
        con.execute("SELECT term, ic FROM annotation_information_content WHERE corpus = ?", [corpus]).fetchall()
    )


def test_writes_each_search_group_as_a_corpus_and_registers_it(kg):
    rows = compute_search_annotation_ic(kg)
    assert [r["corpus"] for r in rows] == [c[0] for c in SEARCH_ANNOTATION_IC_CORPORA]
    con = duckdb.connect(str(kg), read_only=True)
    corpora = dict(con.execute("SELECT corpus, subject_prefixes FROM pheno_comparison_corpora").fetchall())
    # the existing Exomiser corpus row is kept; the three search corpora are added
    assert corpora == {"mondo_hp": ["MONDO"], "hgnc_hp": ["HGNC"], "rgd_mp": ["RGD"], "wb_wbphenotype": ["WB"]}
    # N = 2 human genes (HGNC:3's only edge is negated). HP:1 reaches both, HP:2 only HGNC:1.
    assert _ic(con, "hgnc_hp") == {"HP:1": pytest.approx(0.0), "HP:2": pytest.approx(math.log2(2))}
    assert _ic(con, "wb_wbphenotype")["WBPhenotype:2"] == pytest.approx(0.0)
    assert _ic(con, "mondo_hp") == {"HP:1": 5.0}  # pheno_comparisons' rows untouched


def test_rerunning_replaces_rather_than_duplicates_rows(kg):
    compute_search_annotation_ic(kg)
    compute_search_annotation_ic(kg)
    con = duckdb.connect(str(kg), read_only=True)
    assert con.execute("SELECT count(*) FROM pheno_comparison_corpora").fetchone()[0] == 4
    counts = dict(con.execute("SELECT corpus, count(*) FROM annotation_information_content GROUP BY corpus").fetchall())
    assert counts == {"mondo_hp": 1, "hgnc_hp": 2, "rgd_mp": 1, "wb_wbphenotype": 2}
