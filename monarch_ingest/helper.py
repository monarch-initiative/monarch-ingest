import logging
import os
import sys

import yaml


def file_exists(file):
    return os.path.exists(file) and os.path.getsize(file) > 0

def ingest_output_exists(ingest_config_file, output_dir):
    source = f"./monarch_ingest/{ingest_config_file}"
    with open(source) as sfh:
        ingest_config = yaml.load(sfh, yaml.FullLoader)

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