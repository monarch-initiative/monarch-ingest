"""Smoke tests validating config file integrity for ingests.yaml and qc_expect.yaml."""

from monarch_ingest.utils.ingest_utils import get_ingests, get_qc_expectations, ingest_urls


class TestIngestsYaml:
    def test_loads_successfully(self):
        ingests = get_ingests()
        assert isinstance(ingests, dict)
        assert len(ingests) > 0

    def test_every_ingest_has_known_shape(self):
        ingests = get_ingests()
        for name, entry in ingests.items():
            has_known_shape = "url" in entry or "config" in entry or "repo" in entry
            assert has_known_shape, (
                f"Ingest '{name}' has none of 'url', 'config', or 'repo'"
            )

    def test_repo_entries_have_files_or_metadata_url(self):
        """A `repo:` entry either has `files:` (a transform target) or
        `metadata_url:` (a metadata-only contribution to the build receipt)."""
        ingests = get_ingests()
        for name, entry in ingests.items():
            if "repo" in entry:
                assert entry.get("files") or entry.get("metadata_url"), (
                    f"Ingest '{name}' has 'repo' but neither 'files' nor 'metadata_url'"
                )

    def test_all_urls_are_https(self):
        ingests = get_ingests()
        for name, entry in ingests.items():
            for url in ingest_urls(entry):
                assert url.startswith("https://"), (
                    f"Ingest '{name}' has non-https URL: {url}"
                )

    def test_all_urls_end_with_supported_extension(self):
        """All ingest source URLs must be TSV or JSONL files."""
        ingests = get_ingests()
        for name, entry in ingests.items():
            for url in ingest_urls(entry):
                assert url.endswith(".tsv") or url.endswith(".jsonl"), (
                    f"Ingest '{name}' has URL with unsupported extension: {url}"
                )


class TestQcExpectYaml:
    def test_loads_successfully(self):
        qc = get_qc_expectations()
        assert isinstance(qc, dict)

    def test_has_nodes_and_edges_keys(self):
        qc = get_qc_expectations()
        assert "nodes" in qc
        assert "edges" in qc

    def test_has_provided_by(self):
        qc = get_qc_expectations()
        assert "provided_by" in qc["nodes"]
        assert "provided_by" in qc["edges"]

    def test_every_entry_has_positive_min(self):
        qc = get_qc_expectations()
        for type_key in ["nodes", "edges"]:
            for name, entry in qc[type_key]["provided_by"].items():
                assert "min" in entry, f"{type_key} '{name}' missing 'min' key"
                assert entry["min"] > 0, f"{type_key} '{name}' has min <= 0"
