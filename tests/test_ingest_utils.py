"""Tests for monarch_ingest.utils.ingest_utils."""

import os
from unittest.mock import patch

from monarch_ingest.utils.ingest_utils import (
    file_exists,
    ingest_output_exists,
    get_ingests,
    get_qc_expectations,
    get_release_metadata_sources,
    is_metadata_only,
)


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


class TestGetReleaseMetadataSources:
    def test_derives_unique_sources_from_kozahub_entries(self):
        sources = get_release_metadata_sources()
        assert isinstance(sources, list)
        repos = [r for r, _ in sources]
        assert "alliance-ingest" in repos
        assert "ncbi-gene" in repos
        # Deduplicated even though alliance-ingest appears in many transforms.
        assert len(repos) == len(set(repos))
        # maxo-annotation-ingest is not consumed by any transform — must not appear.
        assert "maxo-annotation-ingest" not in repos
        # alliance-disease-association-ingest was an oversight; alliance disease now comes from alliance-ingest.
        assert "alliance-disease-association-ingest" not in repos
        # Default URL when no override.
        alliance_url = dict(sources)["alliance-ingest"]
        assert alliance_url == (
            "https://github.com/monarch-initiative/alliance-ingest/releases/latest/download/release-metadata.yaml"
        )

    def test_metadata_url_override_is_honored(self):
        sources = dict(get_release_metadata_sources())
        # kg-phenio is published to KG-Hub S3, not GitHub releases.
        assert sources.get("kg-phenio") == (
            "https://kg-hub.berkeleybop.io/kg-phenio/current/release-metadata.yaml"
        )


class TestIsMetadataOnly:
    def test_kg_phenio_is_metadata_only(self):
        ingests = get_ingests()
        assert is_metadata_only(ingests["kg_phenio"])

    def test_kozahub_entries_with_files_are_not_metadata_only(self):
        ingests = get_ingests()
        assert not is_metadata_only(ingests["alliance_gene"])


class TestDownloadReleaseMetadata:
    def test_writes_files_skips_404_and_errors(self, tmp_path):
        from unittest.mock import MagicMock
        import requests

        from monarch_ingest.cli_utils import download_release_metadata

        ok_resp = MagicMock(status_code=200, ok=True, content=b"source: foo\n")
        miss_resp = MagicMock(status_code=404, ok=False)
        bad_resp = MagicMock(status_code=500, ok=False)
        custom_resp = MagicMock(status_code=200, ok=True, content=b"source: kg-phenio\n")

        responses = {
            "https://github.com/monarch-initiative/foo/releases/latest/download/release-metadata.yaml": ok_resp,
            "https://github.com/monarch-initiative/missing/releases/latest/download/release-metadata.yaml": miss_resp,
            "https://github.com/monarch-initiative/broken/releases/latest/download/release-metadata.yaml": bad_resp,
            "https://kg-hub.example/kg-phenio/release-metadata.yaml": custom_resp,
        }

        def fake_get(url, **_kwargs):
            if "boom" in url:
                raise requests.ConnectionError("nope")
            return responses[url]

        with patch("monarch_ingest.cli_utils.requests.get", side_effect=fake_get):
            written = download_release_metadata(
                sources=[
                    ("foo", "https://github.com/monarch-initiative/foo/releases/latest/download/release-metadata.yaml"),
                    ("missing", "https://github.com/monarch-initiative/missing/releases/latest/download/release-metadata.yaml"),
                    ("broken", "https://github.com/monarch-initiative/broken/releases/latest/download/release-metadata.yaml"),
                    ("boom", "https://github.com/monarch-initiative/boom/releases/latest/download/release-metadata.yaml"),
                    ("kg-phenio", "https://kg-hub.example/kg-phenio/release-metadata.yaml"),
                ],
                output_dir=str(tmp_path),
            )

        assert written == ["foo", "kg-phenio"]
        assert (tmp_path / "foo.yaml").read_bytes() == b"source: foo\n"
        assert (tmp_path / "kg-phenio.yaml").read_bytes() == b"source: kg-phenio\n"
        assert not (tmp_path / "missing.yaml").exists()
        assert not (tmp_path / "broken.yaml").exists()
        assert not (tmp_path / "boom.yaml").exists()


class TestGetQcExpectations:
    def test_returns_dict(self):
        result = get_qc_expectations()
        assert isinstance(result, dict)
        assert "nodes" in result
        assert "edges" in result
