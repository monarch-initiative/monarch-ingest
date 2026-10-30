"""The `information-content` and `pheno-comparisons` stages end to end, on a tiny synthetic KG."""

import tarfile

import duckdb
import pytest

from monarch_ingest.cli_utils import apply_information_content, build_pheno_comparisons

GENE = "biolink:GeneToPhenotypicFeatureAssociation"
DISEASE = "biolink:DiseaseToPhenotypicFeatureAssociation"
# term -> direct superclasses; UPHENO:X groups HP:1, MP:1 and ZP:1
PARENTS = {
    "HP:1": ["HP:0000118", "UPHENO:X"],
    "HP:2": ["HP:0000118"],
    "MP:1": ["MP:0000001", "UPHENO:X"],
    "MP:2": ["MP:0000001"],
    "ZP:1": ["ZP:0000000", "UPHENO:X"],
    "ZP:2": ["ZP:0000000"],
    "HP:0000118": [],
    "MP:0000001": [],
    "ZP:0000000": [],
    "UPHENO:X": [],
}
# four entities per corpus, one of them reaching term 1
EDGES = (
    [("MONDO:1", "HP:1", DISEASE)]
    + [(f"MONDO:{i}", "HP:2", DISEASE) for i in (2, 3, 4)]
    + [("MGI:1", "MP:1", GENE)]
    + [(f"MGI:{i}", "MP:2", GENE) for i in (2, 3, 4)]
    + [("ZFIN:1", "ZP:1", GENE)]
    + [(f"ZFIN:{i}", "ZP:2", GENE) for i in (2, 3, 4)]
    + [("HGNC:1", "HP:1", GENE), ("HGNC:2", "HP:2", GENE)]
    + [("RGD:1", "MP:1", GENE)]
    + [("WB:1", "WBPhenotype:1", GENE)]  # every search group needs annotations, or the stage fails
)


def _ancestors(term):
    out, todo = {term}, list(PARENTS[term])
    while todo:
        a = todo.pop()
        if a not in out:
            out.add(a)
            todo.extend(PARENTS[a])
    return out


@pytest.fixture
def output_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # the stages write data/ and output/ relative to the working directory
    out = tmp_path / "output"
    out.mkdir()
    con = duckdb.connect(str(out / "monarch-kg.duckdb"))
    con.execute("CREATE TABLE closure (subject_id VARCHAR, predicate_id VARCHAR, object_id VARCHAR)")
    for t in PARENTS:
        for a in _ancestors(t):
            con.execute("INSERT INTO closure VALUES (?, 'rdfs:subClassOf', ?)", [t, a])
    con.execute("""CREATE TABLE edges (id VARCHAR, subject VARCHAR, predicate VARCHAR, object VARCHAR,
           category VARCHAR, negated VARCHAR)""")
    for i, (s, o, cat) in enumerate(EDGES):
        con.execute("INSERT INTO edges VALUES (?, ?, 'biolink:has_phenotype', ?, ?, 'False')", [f"e{i}", s, o, cat])
    con.execute("CREATE TABLE nodes (id VARCHAR, name VARCHAR)")
    con.executemany("INSERT INTO nodes VALUES (?, ?)", [[t, f"label {t}"] for t in PARENTS])
    con.close()
    return out


def test_information_content_then_pheno_comparisons(output_dir):
    apply_information_content(output_dir=str(output_dir))
    con = duckdb.connect(str(output_dir / "monarch-kg.duckdb"), read_only=True)
    tables = {r[0] for r in con.execute("SHOW TABLES").fetchall()}
    corpora = {r[0] for r in con.execute("SELECT corpus FROM pheno_comparison_corpora").fetchall()}
    con.close()
    assert {"information_content", "closure_size", "annotation_information_content"} <= tables
    assert corpora == {"mondo_hp", "mgi_mp", "zfin_zp", "hgnc_hp", "rgd_mp", "wb_wbphenotype"}

    build_pheno_comparisons("2026-10-07", output_dir=str(output_dir), metadata_dir="no-such-dir", threads=1)
    tarballs = sorted(p.name for p in (output_dir / "pheno-comparisons").iterdir())
    assert tarballs == [
        "HP_vs_HP_semsimian_phenio_kg-2026-10-07.tsv.tar.gz",
        "HP_vs_MP_semsimian_phenio_kg-2026-10-07.tsv.tar.gz",
        "HP_vs_ZP_semsimian_phenio_kg-2026-10-07.tsv.tar.gz",
    ]
    with tarfile.open(output_dir / "pheno-comparisons" / tarballs[1]) as tf:
        assert any(n.endswith(".tsv") for n in tf.getnames()) and "mpa_ic.tsv" in tf.getnames()


def test_pheno_comparisons_before_information_content_fails(output_dir):
    with pytest.raises(RuntimeError, match="information-content"):
        build_pheno_comparisons("2026-10-07", output_dir=str(output_dir), metadata_dir="no-such-dir")
