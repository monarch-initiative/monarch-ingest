import os, sys, pkgutil
import logging
import yaml


def get_ingests():
    return yaml.safe_load(pkgutil.get_data(__name__, 'ingests.yaml'))


def get_ingest(source: str):
    ingests = get_ingests
    return yaml.load(
        pkgutil.get_data(__name__, ingests[source]['config']), yaml.FullLoader
    )


def file_exists(file):
    return os.path.exists(file) and os.path.getsize(file) > 0


def ingest_output_exists(source, output_dir):
    ingests = get_ingests()

    ingest_config = yaml.load(
        pkgutil.get_data(__name__, ingests[source]['config']), yaml.FullLoader
    )

    #print(f"Ingest config: {ingest_config}\n{type(ingest_config)}")

    has_node_properties = "node_properties" in ingest_config
    has_edge_properties = "edge_properties" in ingest_config

    nodes_file = f"{output_dir}/{ingest_config['name']}_nodes.tsv"
    edges_file = f"{output_dir}/{ingest_config['name']}_edges.tsv"

    if has_node_properties and not file_exists(nodes_file):
        return False
    if has_edge_properties and not file_exists(edges_file):
        return False

    return True


def get_logger(name: str) -> logging.Logger:
    """Get an instance of logger."""
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(":%(name)-12s: %(levelname)-6s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    return logger