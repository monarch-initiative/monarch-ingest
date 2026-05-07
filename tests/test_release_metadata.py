"""Tests for monarch_ingest.release_metadata."""

import yaml

from monarch_ingest.release_metadata import (
    aggregate,
    find_disagreements,
)


def _write(p, doc):
    p.write_text(yaml.safe_dump(doc, sort_keys=False))


def test_find_disagreements_flags_tagged_version_skew():
    docs = [
        {"id": "a", "sources": [{"id": "infores:hgnc", "version": "2026-04-01", "version_method": "url_path"}]},
        {"id": "b", "sources": [{"id": "infores:hgnc", "version": "2026-05-01", "version_method": "url_path"}]},
        {"id": "c", "sources": [{"id": "infores:agr", "version": "8.3.0", "version_method": "alliance_fms_api"}]},
    ]
    disagreements, drift = find_disagreements(docs)
    assert drift == []
    assert len(disagreements) == 1
    d = disagreements[0]
    assert d["id"] == "infores:hgnc"
    assert d["versions_observed"] == ["2026-04-01", "2026-05-01"]
    assert d["by_ingest"] == {"a": "2026-04-01", "b": "2026-05-01"}


def test_find_disagreements_buckets_rolling_drift_separately():
    docs = [
        {"id": "a", "sources": [{"id": "infores:ncbi-gene", "version": "2026-05-01", "version_method": "http_last_modified"}]},
        {"id": "b", "sources": [{"id": "infores:ncbi-gene", "version": "2026-05-02", "version_method": "http_last_modified"}]},
    ]
    disagreements, drift = find_disagreements(docs)
    assert disagreements == []
    assert len(drift) == 1
    assert drift[0]["id"] == "infores:ncbi-gene"


def test_find_disagreements_mixed_methods_treated_as_hard():
    # If even one consumer captured the source via a tagged method, treat as a real disagreement.
    docs = [
        {"id": "a", "sources": [{"id": "infores:foo", "version": "1", "version_method": "http_last_modified"}]},
        {"id": "b", "sources": [{"id": "infores:foo", "version": "2", "version_method": "url_path"}]},
    ]
    disagreements, drift = find_disagreements(docs)
    assert drift == []
    assert len(disagreements) == 1


def test_find_disagreements_clean_when_versions_match():
    docs = [
        {"id": "a", "sources": [{"id": "infores:hgnc", "version": "2026-05-01", "version_method": "url_path"}]},
        {"id": "b", "sources": [{"id": "infores:hgnc", "version": "2026-05-01", "version_method": "url_path"}]},
    ]
    assert find_disagreements(docs) == ([], [])


def test_aggregate_emits_release_shape(tmp_path):
    _write(tmp_path / "alliance-ingest.yaml", {
        "id": "alliance-ingest",
        "version": "8.3.0",
        "transform_version": "abc",
        "biolink_version": "4.3.9",
        "build_version": "alliance-ingest_8.3.0_abc_4.3.9",
        "generated_at": "2026-05-02T00:00:00Z",
        "sources": [{"id": "infores:agr", "version": "8.3.0", "urls": ["https://example.org/x"]}],
        "artifacts": [{"path": "alliance_gene_nodes.tsv", "sha256": "deadbeef"}],
        "tools": {"koza": "2.3.0"},
    })

    receipt = aggregate(
        input_dir=tmp_path,
        kg_name="monarch-kg",
        kg_version="2026-05-02",
        packages={"biolink": "4.3.9", "koza": "2.3.0"},
        artifacts=[{"path": "monarch-kg.tar.gz", "sha256": "cafef00d"}],
    )

    assert receipt["id"] == "monarch-kg"
    assert receipt["version"] == "2026-05-02"
    assert receipt["packages"] == {"biolink": "4.3.9", "koza": "2.3.0"}
    assert receipt["artifacts"][0]["path"] == "monarch-kg.tar.gz"
    assert len(receipt["sources"]) == 1

    nested = receipt["sources"][0]
    assert nested["id"] == "alliance-ingest"
    assert nested["version"] == "8.3.0"
    assert nested["sources"][0]["id"] == "infores:agr"
    assert receipt["disagreements"] == []
    assert receipt["version_drift"] == []


def test_aggregate_handles_kg_phenio_recursive_shape(tmp_path):
    """kg-phenio's release-metadata.yaml has phenio nested as a Release whose
    own sources are the upstream ontologies — verify the aggregator preserves
    the recursive structure verbatim under monarch-kg."""
    _write(tmp_path / "kg-phenio.yaml", {
        "id": "kg-phenio",
        "version": "v2026-05-06",
        "transform_version": "deadbeef",
        "biolink_version": "4.3.9",
        "build_version": "kg-phenio_v2026-05-06_deadbeef_4.3.9",
        "generated_at": "2026-05-06T00:00:00Z",
        "sources": [
            {
                "id": "phenio",
                "name": "PHENIO",
                "version": "v2026-05-06",
                "version_method": "github_release_api",
                "sources": [
                    {"id": "infores:bfo", "version": "2019-08-26", "version_method": "owl_version_iri"},
                    {"id": "infores:chebi", "version": "2026-04-20", "version_method": "owl_version_iri"},
                ],
            },
        ],
    })

    receipt = aggregate(
        input_dir=tmp_path,
        kg_name="monarch-kg",
        kg_version="2026-05-06",
    )

    assert len(receipt["sources"]) == 1
    kgp = receipt["sources"][0]
    assert kgp["id"] == "kg-phenio"
    # Phenio's nested ontology Releases survive verbatim under kg-phenio.
    phenio = kgp["sources"][0]
    assert phenio["id"] == "phenio"
    assert {s["id"] for s in phenio["sources"]} == {"infores:bfo", "infores:chebi"}
