import pytest


@pytest.fixture(scope="package")
def global_table():
    return "src/monarch_ingest/translation_table.yaml"


@pytest.fixture
def taxon_label_map_cache():
    return {
        "taxon-labels": {
            "NCBITaxon:7955": {"label": "Danio rerio"},
            "NCBITaxon:6239": {"label": "Caenorhabditis elegans"},
            "NCBITaxon:44689": {"label": "Dictyostelium discoideum"},
            "NCBITaxon:9606": {"label": "Homo sapiens"},
            "NCBITaxon:4896": {"label": "Schizosaccharomyces pombe"},
            "NCBITaxon:9615": {"label": "Canis lupus familiaris"},
            "NCBITaxon:9913": {"label": "Bos taurus"},
            "NCBITaxon:9823": {"label": "Sus scrofa"},
            "NCBITaxon:9031": {"label": "Gallus gallus"},
        }
    }
