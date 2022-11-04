import os, pkgutil
from pathlib import Path
import yaml


def get_ingests():
    return yaml.safe_load(pkgutil.get_data("monarch_ingest", 'ingests.yaml'))


def get_ingest(source: str):
    ingests = get_ingests
    return yaml.load(
        pkgutil.get_data("monarch_ingest", ingests[source]['config']), yaml.FullLoader
    )


def file_exists(file):
    return (Path(file).is_file() and os.stat(file).st_size > 1000)


def ingest_output_exists(source, output_dir):
    ingests = get_ingests()

    ingest_config = yaml.load(
        pkgutil.get_data("monarch_ingest", ingests[source]['config']), yaml.FullLoader
    )

    has_node_properties = "node_properties" in ingest_config
    has_edge_properties = "edge_properties" in ingest_config

    nodes_file = f"{output_dir}/{ingest_config['name']}_nodes.tsv"
    edges_file = f"{output_dir}/{ingest_config['name']}_edges.tsv"

    if has_node_properties and not file_exists(nodes_file):
        return False
    if has_edge_properties and not file_exists(edges_file):
        return False

    return True

