"""Tests for the extracted validate_qc_counts function."""

from monarch_ingest.utils.ingest_utils import validate_qc_counts


def _make_report(nodes=None, edges=None):
    """Helper to build a qc_report dict."""
    return {
        "nodes": [{"name": k, "total_number": v} for k, v in (nodes or {}).items()],
        "edges": [{"name": k, "total_number": v} for k, v in (edges or {}).items()],
    }


def _make_expectations(nodes=None, edges=None):
    """Helper to build an expected_counts dict."""
    return {
        "nodes": {"provided_by": {k: {"min": v} for k, v in (nodes or {}).items()}},
        "edges": {"provided_by": {k: {"min": v} for k, v in (edges or {}).items()}},
    }


class TestValidateQcCounts:
    def test_all_counts_pass(self, sample_qc_report, sample_qc_expectations):
        """When all counts meet or exceed expectations, no error."""
        assert validate_qc_counts(sample_qc_report, sample_qc_expectations) is False

    def test_warning_band(self, capsys):
        """Counts below expected but >= 70% should warn, not error."""
        report = _make_report(nodes={"x_nodes": 750}, edges={})
        expectations = _make_expectations(nodes={"x_nodes": 1000}, edges={})
        result = validate_qc_counts(report, expectations)
        assert result is False
        captured = capsys.readouterr()
        assert "Expected x_nodes" in captured.err

    def test_error_band(self):
        """Counts below 70% of expected should error."""
        report = _make_report(nodes={"x_nodes": 600}, edges={})
        expectations = _make_expectations(nodes={"x_nodes": 1000}, edges={})
        result = validate_qc_counts(report, expectations)
        assert result is True

    def test_missing_key(self, capsys):
        """Key in expectations but not in report should error."""
        report = _make_report(nodes={}, edges={})
        expectations = _make_expectations(nodes={"missing_nodes": 1000}, edges={})
        result = validate_qc_counts(report, expectations)
        assert result is True
        captured = capsys.readouterr()
        assert "missing_nodes not found" in captured.err

    def test_exactly_at_70_percent(self):
        """Exactly at 70% boundary — current code has a gap: not < expected*0.7,
        not > expected*0.7, so it falls through with no warning or error."""
        report = _make_report(nodes={"x_nodes": 700}, edges={})
        expectations = _make_expectations(nodes={"x_nodes": 1000}, edges={})
        # 700 == 1000 * 0.7, so:
        #   counts[key] < expected (700 < 1000) → True
        #   counts[key] > way_less_than_expected (700 > 700) → False
        # Falls to elif: counts[key] < expected * 0.7 (700 < 700) → False
        # Neither branch fires — no error.
        result = validate_qc_counts(report, expectations)
        assert result is False

    def test_count_of_zero(self):
        """Zero count should trigger error (well below 70%)."""
        report = _make_report(nodes={"x_nodes": 0}, edges={})
        expectations = _make_expectations(nodes={"x_nodes": 1000}, edges={})
        result = validate_qc_counts(report, expectations)
        assert result is True

    def test_mixed_warnings_and_errors(self):
        """One key warns, another errors — overall should be error."""
        report = _make_report(
            nodes={"warn_nodes": 750, "fail_nodes": 100},
            edges={},
        )
        expectations = _make_expectations(
            nodes={"warn_nodes": 1000, "fail_nodes": 1000},
            edges={},
        )
        result = validate_qc_counts(report, expectations)
        assert result is True

    def test_empty_expectations(self):
        """No expectations means no errors."""
        report = _make_report(nodes={"x_nodes": 100}, edges={"x_edges": 100})
        expectations = _make_expectations(nodes={}, edges={})
        result = validate_qc_counts(report, expectations)
        assert result is False

    def test_nodes_and_edges_both_checked(self):
        """Error in edges should flag even if nodes are fine."""
        report = _make_report(
            nodes={"ok_nodes": 1000},
            edges={"bad_edges": 50},
        )
        expectations = _make_expectations(
            nodes={"ok_nodes": 1000},
            edges={"bad_edges": 1000},
        )
        result = validate_qc_counts(report, expectations)
        assert result is True

    def test_counts_above_expected(self):
        """Counts exceeding expected is fine — no error, no warning."""
        report = _make_report(nodes={"x_nodes": 5000}, edges={})
        expectations = _make_expectations(nodes={"x_nodes": 1000}, edges={})
        result = validate_qc_counts(report, expectations)
        assert result is False

    def test_count_exactly_at_expected(self):
        """Counts exactly matching expected should pass cleanly."""
        report = _make_report(nodes={"x_nodes": 1000}, edges={})
        expectations = _make_expectations(nodes={"x_nodes": 1000}, edges={})
        result = validate_qc_counts(report, expectations)
        assert result is False
