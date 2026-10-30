"""Annotation IC for the Monarch API's phenotype search groups (monarch-app #1475)."""

import math

import duckdb
import pytest
from pheno_comparisons import compute_information_content_tables

from monarch_ingest.cli_utils import compute_search_annotation_ic, search_annotation_corpora

G2P = "biolink:GeneToPhenotypicFeatureAssociation"
D2P = "biolink:DiseaseToPhenotypicFeatureAssociation"
GENOTYPE = "biolink:GenotypeToPhenotypicFeatureAssociation"

CLOSURE = [
    ("HP:1", "HP:1"),
    ("HP:2", "HP:2"),
    ("HP:2", "HP:1"),
    ("MP:1", "MP:1"),
    ("MP:2", "MP:2"),
    ("MP:2", "MP:1"),
    ("ZP:1", "ZP:1"),
    ("WBPhenotype:1", "WBPhenotype:1"),
    ("WBPhenotype:2", "WBPhenotype:2"),
    ("WBPhenotype:2", "WBPhenotype:1"),
]
# (subject, object, category, negated), with negated as the KG stores it: 'True' / 'False' / NULL
EDGES = [
    # human genes: N = 2. HP:1 reaches both, HP:2 only HGNC:1
    ("HGNC:1", "HP:2", G2P, "False"),
    ("HGNC:2", "HP:1", G2P, None),
    ("HGNC:3", "HP:2", G2P, "True"),  # negated: excluded
    ("HGNC:4", "MP:1", G2P, "False"),  # wrong object prefix: excluded
    ("HGNC:5", "HP:1", D2P, "False"),  # disease category (monarch-app#1490): excluded
    # rat genes: N = 2. MP:1 reaches both, MP:2 only RGD:1
    ("RGD:1", "MP:2", G2P, "False"),
    ("RGD:2", "MP:1", G2P, "False"),
    ("RGD:3", "MP:2", GENOTYPE, "False"),  # genotype category: excluded
    # worm genes: N = 2, both on WBPhenotype:2
    ("WB:1", "WBPhenotype:2", G2P, "False"),
    ("WB:2", "WBPhenotype:2", G2P, "False"),
    ("WB:3", "HP:1", G2P, "False"),  # wrong object prefix: excluded
    # the Exomiser corpora pheno_comparisons builds
    ("MONDO:1", "HP:1", D2P, "False"),
    ("MGI:1", "MP:1", G2P, "False"),
    ("ZFIN:1", "ZP:1", G2P, "False"),
]


def _write_kg(path, edges=EDGES):
    con = duckdb.connect(str(path))
    con.execute("CREATE TABLE closure(subject_id VARCHAR, predicate_id VARCHAR, object_id VARCHAR)")
    con.executemany("INSERT INTO closure VALUES (?, 'rdfs:subClassOf', ?)", CLOSURE)
    con.execute(
        "CREATE TABLE edges(subject VARCHAR, predicate VARCHAR, object VARCHAR, category VARCHAR, negated VARCHAR)"
    )
    con.executemany("INSERT INTO edges VALUES (?, 'biolink:has_phenotype', ?, ?, ?)", edges)
    con.close()
    return path


@pytest.fixture
def kg(tmp_path):
    return _write_kg(tmp_path / "monarch-kg.duckdb")


def _ic(con, corpus):
    return dict(
        con.execute("SELECT term, ic FROM annotation_information_content WHERE corpus = ?", [corpus]).fetchall()
    )


def test_writes_each_search_group_as_a_corpus_and_registers_it(kg):
    compute_information_content_tables(kg)  # the order the information-content stage runs them in
    rows = compute_search_annotation_ic(kg)
    assert [r["corpus"] for r in rows] == [c.key for c in search_annotation_corpora()]
    assert {r["corpus"]: r["entity_count"] for r in rows} == {"hgnc_hp": 2, "rgd_mp": 2, "wb_wbphenotype": 2}
    con = duckdb.connect(str(kg), read_only=True)
    registry = dict(con.execute("SELECT corpus, subject_prefixes FROM pheno_comparison_corpora").fetchall())
    assert registry == {
        "mondo_hp": ["MONDO"],
        "mgi_mp": ["MGI"],
        "zfin_zp": ["ZFIN"],
        "hgnc_hp": ["HGNC"],
        "rgd_mp": ["RGD"],
        "wb_wbphenotype": ["WB"],
    }
    assert _ic(con, "hgnc_hp") == {"HP:1": pytest.approx(0.0), "HP:2": pytest.approx(math.log2(2))}
    assert _ic(con, "rgd_mp") == {"MP:1": pytest.approx(0.0), "MP:2": pytest.approx(math.log2(2))}
    assert _ic(con, "wb_wbphenotype") == {"WBPhenotype:1": pytest.approx(0.0), "WBPhenotype:2": pytest.approx(0.0)}


def test_search_corpora_survive_a_pheno_comparisons_rerun(kg):
    """Rerunning `pheno-comparisons information-content` on a built KG must not unregister these corpora."""
    compute_information_content_tables(kg)
    compute_search_annotation_ic(kg)
    compute_information_content_tables(kg)
    con = duckdb.connect(str(kg), read_only=True)
    registered = sorted(r[0] for r in con.execute("SELECT corpus FROM pheno_comparison_corpora").fetchall())
    with_ic = sorted(r[0] for r in con.execute("SELECT DISTINCT corpus FROM annotation_information_content").fetchall())
    assert registered == with_ic == ["hgnc_hp", "mgi_mp", "mondo_hp", "rgd_mp", "wb_wbphenotype", "zfin_zp"]


def test_rerunning_replaces_rather_than_duplicates_rows(kg):
    compute_search_annotation_ic(kg)
    compute_search_annotation_ic(kg)
    con = duckdb.connect(str(kg), read_only=True)
    assert con.execute("SELECT count(*) FROM pheno_comparison_corpora").fetchone()[0] == 3
    counts = dict(con.execute("SELECT corpus, count(*) FROM annotation_information_content GROUP BY corpus").fetchall())
    assert counts == {"hgnc_hp": 2, "rgd_mp": 2, "wb_wbphenotype": 2}


def test_a_search_group_without_annotations_fails_the_build(tmp_path):
    kg = _write_kg(tmp_path / "monarch-kg.duckdb", [e for e in EDGES if not e[0].startswith("WB:")])
    with pytest.raises(RuntimeError, match="wb_wbphenotype"):
        compute_search_annotation_ic(kg)
