import os
import pkgutil
from pathlib import Path
import yaml


def get_ingests():
    return yaml.safe_load(pkgutil.get_data("monarch_ingest", "ingests.yaml"))


def get_qc_expectations():
    """Get the QC expectations which tell us what files each ingest should produce"""
    return yaml.safe_load(pkgutil.get_data("monarch_ingest", "qc_expect.yaml"))


def file_exists(file):
    return Path(file).is_file() and os.stat(file).st_size > 1000


def ingest_output_exists(source, output_dir):
    """Check if ingest output files exist using QC expectations as the source of truth"""
    qc_expectations = get_qc_expectations()

    # Check if this ingest should produce nodes
    nodes_key = f"{source}_nodes"
    expects_nodes = nodes_key in qc_expectations.get("nodes", {}).get("provided_by", {})

    # Check if this ingest should produce edges
    edges_key = f"{source}_edges"
    expects_edges = edges_key in qc_expectations.get("edges", {}).get("provided_by", {})

    nodes_file = f"{output_dir}/{source}_nodes.tsv"
    edges_file = f"{output_dir}/{source}_edges.tsv"

    if expects_nodes and not file_exists(nodes_file):
        return False
    if expects_edges and not file_exists(edges_file):
        return False

    return True
