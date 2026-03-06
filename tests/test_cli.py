"""CLI validation tests via typer.testing.CliRunner."""

import sys
from unittest.mock import patch, MagicMock

from typer.testing import CliRunner

from monarch_ingest.main import typer_app

# Ensure cli_utils is resolvable for @patch targets. With deferred imports in
# main.py, cli_utils isn't loaded at import time. When full deps are available
# we import normally; otherwise a MagicMock allows test collection without the
# heavy transitive dependency stack (koza, duckdb, pystow, etc.)
try:
    import monarch_ingest.cli_utils  # noqa: F401
except ImportError:
    sys.modules["monarch_ingest.cli_utils"] = MagicMock()

runner = CliRunner()


class TestTransformValidation:
    def test_no_flags_raises_error(self):
        """transform with no flags should raise ValueError."""
        result = runner.invoke(typer_app, ["transform"])
        assert result.exit_code != 0
        assert "flag must be provided" in result.output or result.exception is not None

    def test_multiple_conflicting_flags_raises_error(self):
        """transform with --ingest and --all should raise ValueError."""
        result = runner.invoke(typer_app, ["transform", "--ingest", "x", "--all"])
        assert result.exit_code != 0

    @patch("monarch_ingest.cli_utils.transform_one")
    def test_ingest_calls_transform_one(self, mock_transform_one):
        result = runner.invoke(typer_app, ["transform", "--ingest", "test_ingest"])
        assert result.exit_code == 0
        mock_transform_one.assert_called_once()
        call_kwargs = mock_transform_one.call_args
        assert call_kwargs.kwargs["ingest"] == "test_ingest"

    @patch("monarch_ingest.cli_utils.transform_all")
    def test_all_calls_transform_all(self, mock_transform_all):
        result = runner.invoke(typer_app, ["transform", "--all"])
        assert result.exit_code == 0
        mock_transform_all.assert_called_once()

    @patch("monarch_ingest.cli_utils.transform_phenio")
    def test_phenio_calls_transform_phenio(self, mock_transform_phenio):
        result = runner.invoke(typer_app, ["transform", "--phenio"])
        assert result.exit_code == 0
        mock_transform_phenio.assert_called_once()


class TestVersion:
    def test_version_flag(self):
        """--version should print the package version."""
        result = runner.invoke(typer_app, ["--version"])
        assert result.exit_code == 0
        assert "monarch_ingest version:" in result.output
