"""Tests for monarch_ingest.utils.source_filters."""

import json

from monarch_ingest.utils.ingest_utils import get_ingests
from monarch_ingest.utils.source_filters import SOURCE_FILTERS, filter_medic


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
            {"id": "e1", "subject": "CHEBI:1", "object": "MONDO:1"},
            {"id": "e2", "subject": "CHEBI:1", "object": "HP:1", "disease_context_qualifier": "MONDO:2"},
            {"id": "e3", "subject": "CHEBI:1", "object": "HP:1", "disease_context_qualifier": "UMLS:C1"},
            {"id": "e4", "subject": "CHEBI:1", "object": "MONDO:1", "disease_context_qualifier": "adults with x"},
            {"id": "e5", "subject": "CHEBI:1", "object": "UMLS:C2"},
        ]
        out, qc = self.run(tmp_path, [], edges)
        assert read_ids(out / "medic_edges.jsonl") == ["e1", "e2", "e5"]
        assert read_ids(qc / "medic_excluded_edges.jsonl") == ["e3", "e4"]

    def test_only_non_chebi_drug_nodes_with_kept_edges(self, tmp_path):
        nodes = [{"id": i} for i in ["CHEBI:1", "MONDO:1", "UMLS:C1", "DRON:1", "RXCUI:1", "UNII:1", "RXCUI:2"]]
        edges = [
            {"id": "e1", "subject": "DRON:1", "object": "MONDO:1"},
            {"id": "e2", "subject": "RXCUI:1", "object": "UMLS:C1"},
            {"id": "e3", "subject": "UNII:1", "object": "MONDO:1"},
            {"id": "e4", "subject": "RXCUI:2", "object": "MONDO:1", "disease_context_qualifier": "free text"},
        ]
        out, _ = self.run(tmp_path, nodes, edges)
        assert read_ids(out / "medic_nodes.jsonl") == ["DRON:1", "RXCUI:1", "UNII:1"]

    def test_lines_are_copied_unchanged(self, tmp_path):
        raw = tmp_path / "raw"
        raw.mkdir()
        line = '{"id": "e1", "subject": "CHEBI:1", "object": "MONDO:1", "medic_approval_date": "20020524"}\n'
        (raw / "medic_edges.jsonl").write_text(line)
        (raw / "medic_nodes.jsonl").write_text("")
        filter_medic(raw, tmp_path / "out", tmp_path / "qc")
        assert (tmp_path / "out" / "medic_edges.jsonl").read_text() == line


def test_ingest_filters_are_registered():
    for name, entry in get_ingests().items():
        if isinstance(entry, dict) and "filter" in entry:
            assert entry["filter"] in SOURCE_FILTERS, name
