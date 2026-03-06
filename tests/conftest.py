"""Shared test fixtures for monarch-ingest tests."""

import pytest


@pytest.fixture
def sample_qc_report():
    """A minimal QC report structure matching qc_report.yaml format."""
    return {
        "nodes": [
            {"name": "alliance_gene_nodes", "total_number": 300000},
            {"name": "hgnc_gene_nodes", "total_number": 45000},
        ],
        "edges": [
            {"name": "go_annotation_edges", "total_number": 2600000},
            {"name": "biogrid_gene_to_gene_edges", "total_number": 1400000},
        ],
    }


@pytest.fixture
def sample_qc_expectations():
    """Matching expected counts for sample_qc_report."""
    return {
        "nodes": {
            "provided_by": {
                "alliance_gene_nodes": {"min": 290000},
                "hgnc_gene_nodes": {"min": 43000},
            }
        },
        "edges": {
            "provided_by": {
                "go_annotation_edges": {"min": 2500000},
                "biogrid_gene_to_gene_edges": {"min": 1340000},
            }
        },
    }
