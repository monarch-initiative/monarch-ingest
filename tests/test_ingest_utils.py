"""Tests for monarch_ingest.utils.ingest_utils."""

import os
from unittest.mock import patch

from monarch_ingest.utils.ingest_utils import file_exists, ingest_output_exists, get_ingests, get_qc_expectations


class TestFileExists:
    def test_missing_file(self, tmp_path):
        assert file_exists(str(tmp_path / "nonexistent.tsv")) is False

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.tsv"
        f.write_text("")
        assert file_exists(str(f)) is False

    def test_too_small_file(self, tmp_path):
        f = tmp_path / "small.tsv"
        f.write_text("x" * 999)
        assert file_exists(str(f)) is False

    def test_boundary_1000_bytes(self, tmp_path):
        """Exactly 1000 bytes should NOT pass — threshold is > 1000."""
        f = tmp_path / "boundary.tsv"
        f.write_text("x" * 1000)
        assert file_exists(str(f)) is False

    def test_boundary_1001_bytes(self, tmp_path):
        f = tmp_path / "big_enough.tsv"
        f.write_text("x" * 1001)
        assert file_exists(str(f)) is True

    def test_large_file(self, tmp_path):
        f = tmp_path / "large.tsv"
        f.write_text("x" * 5000)
        assert file_exists(str(f)) is True


class TestIngestOutputExists:
    def _make_file(self, tmp_path, name, size=2000):
        f = tmp_path / name
        f.write_text("x" * size)

    def test_both_present(self, tmp_path):
        """When QC expects both nodes and edges, and both files exist."""
        self._make_file(tmp_path, "alliance_gene_nodes.tsv")
        self._make_file(tmp_path, "alliance_gene_edges.tsv")
        mock_qc = {
            "nodes": {"provided_by": {"alliance_gene_nodes": {"min": 100}}},
            "edges": {"provided_by": {"alliance_gene_edges": {"min": 100}}},
        }
        with patch("monarch_ingest.utils.ingest_utils.get_qc_expectations", return_value=mock_qc):
            assert ingest_output_exists("alliance_gene", str(tmp_path)) is True

    def test_nodes_missing(self, tmp_path):
        """When QC expects nodes but file is missing."""
        self._make_file(tmp_path, "alliance_gene_edges.tsv")
        mock_qc = {
            "nodes": {"provided_by": {"alliance_gene_nodes": {"min": 100}}},
            "edges": {"provided_by": {"alliance_gene_edges": {"min": 100}}},
        }
        with patch("monarch_ingest.utils.ingest_utils.get_qc_expectations", return_value=mock_qc):
            assert ingest_output_exists("alliance_gene", str(tmp_path)) is False

    def test_edges_missing(self, tmp_path):
        """When QC expects edges but file is missing."""
        self._make_file(tmp_path, "alliance_gene_nodes.tsv")
        mock_qc = {
            "nodes": {"provided_by": {"alliance_gene_nodes": {"min": 100}}},
            "edges": {"provided_by": {"alliance_gene_edges": {"min": 100}}},
        }
        with patch("monarch_ingest.utils.ingest_utils.get_qc_expectations", return_value=mock_qc):
            assert ingest_output_exists("alliance_gene", str(tmp_path)) is False

    def test_no_expectations(self, tmp_path):
        """When QC has no expectations for this source, should return True."""
        mock_qc = {
            "nodes": {"provided_by": {}},
            "edges": {"provided_by": {}},
        }
        with patch("monarch_ingest.utils.ingest_utils.get_qc_expectations", return_value=mock_qc):
            assert ingest_output_exists("unknown_source", str(tmp_path)) is True

    def test_only_nodes_expected(self, tmp_path):
        """When QC only expects nodes (no edges entry), nodes file present."""
        self._make_file(tmp_path, "hgnc_gene_nodes.tsv")
        mock_qc = {
            "nodes": {"provided_by": {"hgnc_gene_nodes": {"min": 100}}},
            "edges": {"provided_by": {}},
        }
        with patch("monarch_ingest.utils.ingest_utils.get_qc_expectations", return_value=mock_qc):
            assert ingest_output_exists("hgnc_gene", str(tmp_path)) is True

    def test_jsonl_edges_detected(self, tmp_path):
        """When edges are .jsonl instead of .tsv, they should still be found."""
        self._make_file(tmp_path, "dismech_edges.jsonl")
        mock_qc = {
            "nodes": {"provided_by": {}},
            "edges": {"provided_by": {"dismech_edges": {"min": 100}}},
        }
        with patch("monarch_ingest.utils.ingest_utils.get_qc_expectations", return_value=mock_qc):
            assert ingest_output_exists("dismech", str(tmp_path)) is True

    def test_jsonl_nodes_detected(self, tmp_path):
        """When nodes are .jsonl instead of .tsv, they should still be found."""
        self._make_file(tmp_path, "some_source_nodes.jsonl")
        mock_qc = {
            "nodes": {"provided_by": {"some_source_nodes": {"min": 100}}},
            "edges": {"provided_by": {}},
        }
        with patch("monarch_ingest.utils.ingest_utils.get_qc_expectations", return_value=mock_qc):
            assert ingest_output_exists("some_source", str(tmp_path)) is True

    def test_jsonl_edges_missing(self, tmp_path):
        """When edges .jsonl is expected but missing, should return False."""
        mock_qc = {
            "nodes": {"provided_by": {}},
            "edges": {"provided_by": {"dismech_edges": {"min": 100}}},
        }
        with patch("monarch_ingest.utils.ingest_utils.get_qc_expectations", return_value=mock_qc):
            assert ingest_output_exists("dismech", str(tmp_path)) is False


class TestGetIngests:
    def test_returns_dict(self):
        result = get_ingests()
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_known_ingest_present(self):
        result = get_ingests()
        assert "hgnc_gene" in result


class TestGetQcExpectations:
    def test_returns_dict(self):
        result = get_qc_expectations()
        assert isinstance(result, dict)
        assert "nodes" in result
        assert "edges" in result
