import os
import pkgutil
from pathlib import Path
import yaml

from monarch_ingest.utils.log_utils import get_logger


def get_ingests():
    return yaml.safe_load(pkgutil.get_data("monarch_ingest", "ingests.yaml"))


def get_qc_expectations():
    """Get the QC expectations which tell us what files each ingest should produce"""
    return yaml.safe_load(pkgutil.get_data("monarch_ingest", "qc_expect.yaml"))


def file_exists(file):
    return Path(file).is_file() and os.stat(file).st_size > 1000


def _output_file_exists(output_dir, base_name):
    """Check if an output file exists with any supported extension (.tsv or .jsonl)."""
    for ext in ('.tsv', '.jsonl'):
        if file_exists(f"{output_dir}/{base_name}{ext}"):
            return True
    return False


def ingest_output_exists(source, output_dir):
    """Check if ingest output files exist using QC expectations as the source of truth"""
    qc_expectations = get_qc_expectations()

    # Check if this ingest should produce nodes
    nodes_key = f"{source}_nodes"
    expects_nodes = nodes_key in qc_expectations.get("nodes", {}).get("provided_by", {})

    # Check if this ingest should produce edges
    edges_key = f"{source}_edges"
    expects_edges = edges_key in qc_expectations.get("edges", {}).get("provided_by", {})

    if expects_nodes and not _output_file_exists(output_dir, f"{source}_nodes"):
        return False
    if expects_edges and not _output_file_exists(output_dir, f"{source}_edges"):
        return False

    return True


def validate_qc_counts(qc_report, expected_counts, logger=None):
    """Validate QC report counts against expected minimums.

    Returns True if there were errors (counts below 70% threshold), False otherwise.
    """
    if logger is None:
        logger = get_logger()

    error = False
    for type in ['nodes', 'edges']:
        counts = {item["name"]: item["total_number"] for item in qc_report[type]}
        for key in expected_counts[type]["provided_by"]:
            expected = expected_counts[type]["provided_by"][key]["min"]
            way_less_than_expected = expected * 0.7
            if key not in counts:
                error = True
                logger.error(f"{type} {key} not found in qc_report.yaml")
            else:
                if counts[key] < expected and counts[key] > way_less_than_expected:
                    logger.warning(f"Expected {key} to have {expected} {type}, only found {counts[key]}")
                elif counts[key] < expected * 0.7:
                    logger.error(f"Expected {key} to have {expected} {type}, only found {counts[key]}")
                    error = True
    return error
