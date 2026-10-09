"""Tests for monarch_ingest.release_notes."""

from monarch_ingest.release_notes import (
    collect_ingest_notes,
    diff_counts,
    diff_sources,
    flatten_sources,
    render_release_notes,
)


def _receipt(sources, **extra):
    return {
        "id": "monarch-kg",
        "version": "2026-06-01",
        "generated_at": "2026-06-01T00:00:00Z",
        "sources": sources,
        **extra,
    }


def test_flatten_sources_collects_nested_infores_leaves():
    receipt = _receipt(
        [
            {
                "id": "alliance-ingest",
                "sources": [
                    {"id": "infores:agr", "version": "8.3.0", "version_method": "alliance_fms_api"},
                ],
            },
            {
                "id": "kg-phenio",
                "sources": [
                    {
                        "id": "phenio",
                        "version": "v2026-05",
                        "sources": [
                            {"id": "infores:mondo", "version": "2026-05-01", "version_method": "owl_version_iri"},
                            {"id": "infores:chebi", "version": "2026-04-20", "version_method": "owl_version_iri"},
                        ],
                    },
                ],
            },
        ]
    )
    flat = flatten_sources(receipt)
    assert set(flat) == {"infores:agr", "infores:mondo", "infores:chebi"}
    assert flat["infores:mondo"]["version"] == "2026-05-01"
    # non-infores container ids (phenio, kg-phenio) are not treated as sources
    assert "phenio" not in flat


def test_diff_sources_splits_rolling_from_stable():
    current = {
        "infores:mondo": {"version": "2026-06-01", "version_method": "owl_version_iri"},
        "infores:ncbi-gene": {"version": "2026-06-02", "version_method": "http_last_modified"},
        "infores:new": {"version": "1.0", "version_method": "url_path"},
    }
    previous = {
        "infores:mondo": {"version": "2026-05-01", "version_method": "owl_version_iri"},
        "infores:ncbi-gene": {"version": "2026-05-30", "version_method": "http_last_modified"},
        "infores:gone": {"version": "0.9", "version_method": "url_path"},
    }
    d = diff_sources(current, previous)
    assert d["added"] == ["infores:new"]
    assert d["removed"] == ["infores:gone"]
    by_id = {c["id"]: c for c in d["changed"]}
    assert by_id["infores:mondo"]["rolling"] is False
    assert by_id["infores:ncbi-gene"]["rolling"] is True
    assert by_id["infores:mondo"]["from"] == "2026-05-01"
    assert by_id["infores:mondo"]["to"] == "2026-06-01"


def test_diff_counts_orders_by_absolute_delta():
    current = {
        "nodes": [
            {"name": "a", "total_number": 100},
            {"name": "b", "total_number": 50},
            {"name": "c", "total_number": 10},  # new
        ]
    }
    previous = {
        "nodes": [
            {"name": "a", "total_number": 90},
            {"name": "b", "total_number": 200},
        ]
    }
    rows = diff_counts(current, previous, "nodes")
    # b dropped 150, a rose 10, c is new (+10). Biggest absolute move first.
    assert [r["name"] for r in rows] == ["b", "a", "c"]
    assert rows[0]["delta"] == -150
    assert rows[2]["from"] is None and rows[2]["to"] == 10


def test_collect_ingest_notes_reads_notes_or_changelog():
    receipt = _receipt(
        [
            {"id": "alliance-ingest", "notes": "  Added allele records.  "},
            {"id": "hgnc-ingest", "changelog": "Switched to monthly release."},
            {"id": "quiet-ingest"},
        ]
    )
    notes = collect_ingest_notes(receipt)
    assert {n["ingest"] for n in notes} == {"alliance-ingest", "hgnc-ingest"}
    assert notes[0]["text"] == "Added allele records."


def test_render_first_release_has_no_diff_sections():
    receipt = _receipt(
        [{"id": "alliance-ingest", "sources": [{"id": "infores:agr", "version": "8.3.0"}]}],
        packages={"biolink": "4.3.9", "koza": "2.3.0"},
    )
    qc = {"summary": {"total_nodes": 100, "total_edges": 200}}
    md = render_release_notes(receipt, qc)
    assert "# monarch-kg 2026-06-01 — release notes" in md
    assert "No previous release available" in md
    assert "## Sources" in md
    assert "`infores:agr`" in md
    # no diff-only sections
    assert "Per-provider" not in md
    assert "Source version changes" not in md


def test_render_with_previous_shows_deltas_and_flags():
    receipt = _receipt(
        [
            {
                "id": "alliance-ingest",
                "sources": [
                    {"id": "infores:agr", "version": "8.4.0", "version_method": "alliance_fms_api"},
                    {"id": "infores:ncbi-gene", "version": "2026-06-02", "version_method": "http_last_modified"},
                ],
            }
        ],
        packages={"biolink": "4.3.9"},
        disagreements=[{"id": "infores:agr", "by_ingest": {"a": "8.4.0", "b": "8.3.0"}}],
    )
    prev_receipt = {
        "id": "monarch-kg",
        "version": "2026-05-01",
        "sources": [
            {
                "id": "alliance-ingest",
                "sources": [
                    {"id": "infores:agr", "version": "8.3.0", "version_method": "alliance_fms_api"},
                    {"id": "infores:ncbi-gene", "version": "2026-05-30", "version_method": "http_last_modified"},
                ],
            }
        ],
    }
    qc = {
        "summary": {"total_nodes": 110, "total_edges": 200},
        "nodes": [{"name": "alliance_gene_nodes", "total_number": 110}],
    }
    prev_qc = {
        "summary": {"total_nodes": 100, "total_edges": 205},
        "nodes": [{"name": "alliance_gene_nodes", "total_number": 100}],
    }

    md = render_release_notes(receipt, qc, prev_receipt, prev_qc)
    assert "Compared against monarch-kg 2026-05-01" in md
    assert "Nodes: 110 (+10)" in md
    assert "Edges: 200 (-5)" in md
    # stable vs rolling split
    assert "### Stable sources" in md
    assert "`infores:agr`: 8.3.0 → 8.4.0" in md
    assert "### Rolling re-pulls" in md
    assert "http_last_modified" in md
    # per-provider table
    assert "## Per-provider node count changes" in md
    assert "alliance_gene_nodes" in md
    # flags
    assert "### Version disagreements" in md
