"""Tests for monarch_ingest.utils.source_filters."""

import json

from monarch_ingest.utils.ingest_utils import get_ingests
from monarch_ingest.utils.source_filters import SOURCE_FILTERS, filter_medic

HIGH = {"medic_pair_reliability": "HIGH"}


def write_jsonl(path, rows):
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))


def read_ids(path):
    return [json.loads(line)["id"] for line in path.read_text().splitlines()]


class TestFilterMedic:
    def run(self, tmp_path, nodes, edges):
        raw = tmp_path / "raw"
        raw.mkdir()
        write_jsonl(raw / "medic_nodes.jsonl", nodes)
        write_jsonl(raw / "medic_edges.jsonl", edges)
        filter_medic(raw, tmp_path / "out", tmp_path / "qc")
        return tmp_path / "out", tmp_path / "qc"

    def test_edges_need_no_context_or_a_mondo_context(self, tmp_path):
        edges = [
            {"id": "e1", "subject": "CHEBI:1", "object": "MONDO:1", **HIGH},
            {"id": "e2", "subject": "CHEBI:1", "object": "HP:1", "disease_context_qualifier": "MONDO:2", **HIGH},
            {"id": "e3", "subject": "CHEBI:1", "object": "HP:1", "disease_context_qualifier": "UMLS:C1", **HIGH},
            {"id": "e4", "subject": "CHEBI:1", "object": "MONDO:1", "disease_context_qualifier": "adults with x", **HIGH},
            {"id": "e5", "subject": "CHEBI:1", "object": "UMLS:C2", **HIGH},
        ]
        out, qc = self.run(tmp_path, [], edges)
        assert read_ids(out / "medic_edges.jsonl") == ["e1", "e2", "e5"]
        assert read_ids(qc / "medic_excluded_edges.jsonl") == ["e3", "e4"]

    def test_edges_need_a_high_reliability_pair(self, tmp_path):
        edges = [
            {"id": "e1", "subject": "CHEBI:1", "object": "MONDO:1", "medic_pair_reliability": "HIGH"},
            {"id": "e2", "subject": "CHEBI:1", "object": "MONDO:2", "medic_pair_reliability": "MEDIUM"},
            {"id": "e3", "subject": "CHEBI:1", "object": "MONDO:3", "medic_pair_reliability": "LOW"},
            {"id": "e4", "subject": "CHEBI:1", "object": "MONDO:4"},
        ]
        out, qc = self.run(tmp_path, [], edges)
        assert read_ids(out / "medic_edges.jsonl") == ["e1"]
        assert read_ids(qc / "medic_excluded_edges.jsonl") == ["e2", "e3", "e4"]

    def test_edges_from_excluded_jurisdictions_are_dropped(self, tmp_path):
        edges = [
            {"id": "e1", "subject": "CHEBI:1", "object": "MONDO:1", "medic_jurisdiction": "USA", **HIGH},
            {"id": "e2", "subject": "CHEBI:1", "object": "MONDO:2", "medic_jurisdiction": "INDIA", **HIGH},
            {"id": "e3", "subject": "CHEBI:1", "object": "MONDO:3", "medic_jurisdiction": "CHINA", **HIGH},
            {"id": "e4", "subject": "CHEBI:1", "object": "MONDO:4", "medic_jurisdiction": "RUSSIA", **HIGH},
            {"id": "e5", "subject": "CHEBI:1", "object": "MONDO:5", **HIGH},
        ]
        out, qc = self.run(tmp_path, [], edges)
        assert read_ids(out / "medic_edges.jsonl") == ["e1", "e5"]
        assert read_ids(qc / "medic_excluded_edges.jsonl") == ["e2", "e3", "e4"]

    def test_kept_nodes_lose_excluded_jurisdictions(self, tmp_path):
        nodes = [
            {
                "id": "DRON:1",
                "medic_approved_jurisdictions": ["europe", "india", "russia", "usa"],
                "medic_approved_authorities": ["EMA", "CDSCO", "MOH_RUSSIA", "FDA"],
                "medic_registration_numbers": ["MOH_RUSSIA:ЛП-002420"],
            },
            {"id": "DRON:2", "medic_approved_jurisdictions": ["usa"]},
        ]
        edges = [
            {"id": "e1", "subject": "DRON:1", "object": "MONDO:1", **HIGH},
            {"id": "e2", "subject": "DRON:2", "object": "MONDO:1", **HIGH},
        ]
        out, _ = self.run(tmp_path, nodes, edges)
        written = [json.loads(line) for line in (out / "medic_nodes.jsonl").read_text().splitlines()]
        assert written == [
            {
                "id": "DRON:1",
                "medic_approved_jurisdictions": ["europe", "usa"],
                "medic_approved_authorities": ["EMA", "FDA"],
            },
            {"id": "DRON:2", "medic_approved_jurisdictions": ["usa"]},
        ]

    def test_only_non_chebi_drug_nodes_with_kept_edges(self, tmp_path):
        nodes = [{"id": i} for i in ["CHEBI:1", "MONDO:1", "UMLS:C1", "DRON:1", "RXCUI:1", "UNII:1", "RXCUI:2"]]
        edges = [
            {"id": "e1", "subject": "DRON:1", "object": "MONDO:1", **HIGH},
            {"id": "e2", "subject": "RXCUI:1", "object": "UMLS:C1", **HIGH},
            {"id": "e3", "subject": "UNII:1", "object": "MONDO:1", **HIGH},
            {"id": "e4", "subject": "RXCUI:2", "object": "MONDO:1", "disease_context_qualifier": "free text", **HIGH},
        ]
        out, _ = self.run(tmp_path, nodes, edges)
        assert read_ids(out / "medic_nodes.jsonl") == ["DRON:1", "RXCUI:1", "UNII:1"]

    def test_lines_are_copied_unchanged(self, tmp_path):
        raw = tmp_path / "raw"
        raw.mkdir()
        line = '{"id": "e1", "subject": "CHEBI:1", "object": "MONDO:1", "medic_pair_reliability": "HIGH", "medic_approval_date": "20020524"}\n'
        (raw / "medic_edges.jsonl").write_text(line)
        (raw / "medic_nodes.jsonl").write_text("")
        filter_medic(raw, tmp_path / "out", tmp_path / "qc")
        assert (tmp_path / "out" / "medic_edges.jsonl").read_text() == line


def test_ingest_filters_are_registered():
    for name, entry in get_ingests().items():
        if isinstance(entry, dict) and "filter" in entry:
            assert entry["filter"] in SOURCE_FILTERS, name
