"""The `dismech-db` stage end to end, on a tiny synthetic dismech release and KG."""

import json

import duckdb
import pytest
import yaml

from monarch_ingest.dismech_db import build_dismech_db, release_tag

DISORDER = {
    "name": "Wilson Disease",
    "disease_term": {"term": {"id": "MONDO:0010200", "label": "Wilson disease"}},
    "pathophysiology": [
        {
            "name": "ATP7B Defect",
            "genes": [{"term": {"id": "hgnc:870", "label": "ATP7B"}}],
            "cell_types": [{"term": {"id": "CL:0000182", "label": "hepatocyte"}}],
            "downstream": [{"target": "Copper Accumulation", "causal_link_type": "DIRECT"}],
        },
        {"name": "Copper Accumulation", "downstream": [{"target": "Cirrhosis"}, {"target": "Renamed Away"}]},
    ],
    "phenotypes": [
        {
            "name": "Cirrhosis",
            "phenotype_term": {"term": {"id": "HP:0001394", "label": "Cirrhosis"}},
            "frequency": "VERY_FREQUENT",
            "diagnostic": True,
            "evidence": [{"reference": "PMID:1", "supports": "SUPPORT", "snippet": "cirrhosis"}],
        }
    ],
    "treatments": [
        {
            "name": "Trientine",
            "therapeutic_modality": "SMALL_MOLECULE",
            "treatment_term": {"therapeutic_agent": [{"term": {"id": "CHEBI:39501", "label": "trientine"}}]},
            "target_mechanisms": [{"target": "Copper Accumulation", "treatment_effect": "INHIBITS"}],
        }
    ],
}

GRAPH = {
    "nodes": [
        {"id": "ATP7B Defect", "node_type": "pathophysiology", "meta": {"gene_terms": [{"id": "hgnc:870"}]}},
        {"id": "Cirrhosis", "node_type": "phenotype", "meta": {"term_id": "HP:0001394"}},
    ],
    "edges": [{"source": "ATP7B Defect", "target": "Cirrhosis", "predicate": "causes"}],
    "orphan_targets": [],
}


@pytest.fixture
def release(tmp_path):
    kb = tmp_path / "dismech"
    (kb / "kb/disorders").mkdir(parents=True)
    (kb / "kb/disorders/Wilson_Disease.yaml").write_text(yaml.safe_dump(DISORDER))
    (kb / "kb/disorders/Wilson_Disease.history.yaml").write_text("[]")
    graphs = tmp_path / "pathographs"
    graphs.mkdir()
    (graphs / "index.json").write_text(
        json.dumps({"MONDO:0010200": [{"file": "MONDO_0010200.json", "name": "Wilson Disease", "slug": "Wilson"}]})
    )
    (graphs / "by_gene.json").write_text(json.dumps({"hgnc:870": ["MONDO:0010200"]}))
    (graphs / "MONDO_0010200.json").write_text(json.dumps(GRAPH))
    manifest = tmp_path / "release_manifest.json"
    manifest.write_text(json.dumps({"release_tag": "v0.1.47"}))

    kg = tmp_path / "monarch-kg.duckdb"
    con = duckdb.connect(str(kg))
    con.execute(
        "CREATE TABLE _solr_edges AS SELECT * FROM (VALUES "
        "('MONDO:0010200', 'Wilson disease', 'biolink:has_phenotype', 'HP:0001392', 'Abnormality of the liver',"
        " NULL, 'infores:omim', 'OMIM:277900', NULL, NULL, NULL, '2', '2', NULL, NULL, [], []),"
        "('MONDO:0000001', 'other', 'biolink:has_phenotype', 'HP:0001394', 'Cirrhosis',"
        " 'true', 'infores:orphanet', 'ORPHA:1', NULL, NULL, NULL, NULL, NULL, NULL, NULL, [], []),"
        "('HGNC:870', 'ATP7B', 'biolink:has_phenotype', 'HP:0001394', 'Cirrhosis',"
        " NULL, 'infores:hpo', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, [], [])"
        ") t(subject, subject_label, predicate, object, object_label, negated, primary_knowledge_source,"
        " original_subject, frequency_qualifier, frequency_qualifier_label, has_percentage, has_count, has_total,"
        " onset_qualifier_label, sex_qualifier_label, publications, has_evidence)"
    )
    con.execute(
        "CREATE TABLE closure AS SELECT * FROM (VALUES "
        "('HP:0001394', 'rdfs:subClassOf', 'HP:0001394'), ('HP:0001394', 'rdfs:subClassOf', 'HP:0001392'),"
        "('HP:0001392', 'rdfs:subClassOf', 'HP:0001392'), ('HP:0001394', 'rdfs:subClassOf', 'UPHENO:1')"
        ") t(subject_id, predicate_id, object_id)"
    )
    con.execute(
        "CREATE TABLE nodes AS SELECT * FROM (VALUES "
        "('HGNC:870', 'ATP7B', 'biolink:Gene'), ('CL:0000182', 'hepatocyte', 'biolink:Cell'),"
        "('CHEBI:39501', 'trientine', 'biolink:ChemicalEntity'), ('HP:0001394', 'Cirrhosis', 'x')"
        ") t(id, name, category)"
    )
    con.close()
    return {"kb": kb, "pathographs": graphs, "manifest": manifest, "kg": kg, "out": tmp_path / "dismech.duckdb"}


@pytest.fixture
def db(release):
    build_dismech_db(
        release["kb"], release["pathographs"], release["kg"], release["out"], release_tag(release["manifest"])
    )
    con = duckdb.connect(str(release["out"]), read_only=True)
    yield con
    con.close()


def rows(con, sql):
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def test_release_is_recorded(db):
    assert db.execute("SELECT release FROM core.release").fetchone()[0] == "v0.1.47"


def test_history_files_are_skipped(db):
    assert db.execute("SELECT disorder_file FROM core.disorder").fetchall() == [("Wilson_Disease",)]


def test_phenotype_carries_its_upstream_chain(db):
    [p] = rows(db, "SELECT * FROM core.phenotype")
    assert (p["mondo_id"], p["hpo_id"], p["frequency_hp"], p["diagnostic"]) == (
        "MONDO:0010200",
        "HP:0001394",
        "HP:0040281",
        True,
    )
    assert {(e["source"], e["target"]) for e in p["upstream_edges"]} == {
        ("dismech:Wilson_Disease#ATP7B_Defect", "dismech:Wilson_Disease#Copper_Accumulation"),
        ("dismech:Wilson_Disease#Copper_Accumulation", "dismech:Wilson_Disease#Cirrhosis"),
    }
    assert p["nearest_mechanisms"] == ["Copper Accumulation"]


def test_dangling_targets_are_flagged_not_dropped(db):
    resolved = dict(db.execute("SELECT target_id, target_resolved FROM core.causal_edge").fetchall())
    assert resolved["dismech:Wilson_Disease#Renamed_Away"] is False
    assert resolved["dismech:Wilson_Disease#Cirrhosis"] is True


def test_descriptor_prefixes_match_the_kg(db):
    terms = {r[0] for r in db.execute("SELECT term_id FROM core.descriptor").fetchall()}
    assert terms == {"HGNC:870", "CL:0000182"}
    kg = {r[0] for r in db.execute("SELECT id FROM app.kg_node").fetchall()}
    assert kg == {"HGNC:870", "CL:0000182", "CHEBI:39501"}


def test_treatment_agents_and_targets(db):
    [t] = rows(db, "SELECT * FROM core.treatment")
    assert [a["id"] for a in t["agents"]] == ["CHEBI:39501"]
    assert [(m["name"], m["effect"], m["resolved"]) for m in t["target_mechanisms"]] == [
        ("Copper Accumulation", "INHIBITS", True)
    ]


def test_phenotype_mechanism_lists_every_upstream_node(db):
    nodes = {r[0] for r in db.execute("SELECT node_id FROM core.phenotype_mechanism").fetchall()}
    assert nodes == {"dismech:Wilson_Disease#ATP7B_Defect", "dismech:Wilson_Disease#Copper_Accumulation"}


def test_pathograph_tables(db):
    assert db.execute("SELECT mondo_id, file FROM core.pathograph_disorder").fetchall() == [
        ("MONDO:0010200", "MONDO_0010200.json")
    ]
    assert db.execute("SELECT gene_id FROM core.pathograph_gene").fetchall() == [("HGNC:870",)]
    meta = db.execute("SELECT meta FROM core.pathograph_node WHERE id = 'Cirrhosis'").fetchone()[0]
    assert json.loads(meta) == {"term_id": "HP:0001394"}


def test_kg_slices_are_disease_phenotypes_only(db):
    kg = rows(db, "SELECT subject, object, negated FROM app.kg_disease_phenotype ORDER BY subject")
    assert [(r["subject"], r["object"]) for r in kg] == [
        ("MONDO:0000001", "HP:0001394"),
        ("MONDO:0010200", "HP:0001392"),
    ]
    assert db.execute("SELECT count(*) FROM app.kg_phenotype_disease").fetchone()[0] == 2


def test_hp_closure_keeps_hp_ancestors_only(db):
    ancestors = {
        r[0] for r in db.execute("SELECT ancestor_id FROM app.hp_closure WHERE hpo_id = 'HP:0001394'").fetchall()
    }
    assert ancestors == {"HP:0001394", "HP:0001392"}


def test_reads_release_zips(release, tmp_path):
    import shutil

    kb_zip = shutil.make_archive(str(tmp_path / "kb"), "zip", release["kb"], "kb")
    graphs_zip = shutil.make_archive(str(tmp_path / "graphs"), "zip", tmp_path, "pathographs")
    out = tmp_path / "from-zip.duckdb"
    build_dismech_db(kb_zip, graphs_zip, release["kg"], out, "v0")
    con = duckdb.connect(str(out), read_only=True)
    assert con.execute("SELECT count(*) FROM core.phenotype").fetchone()[0] == 1
    assert con.execute("SELECT count(*) FROM core.pathograph_node").fetchone()[0] == 2
