import glob
import os
import tarfile
from typing import List, Optional

import pandas as pd
import yaml
from kgx.cli.cli_utils import transform as kgx_transform
from koza.cli_runner import transform_source
from koza.model.config.source_config import OutputFormat

from monarch_ingest.helper import *

LOG = get_logger(__name__)

OUTPUT_DIR = "output"

def transform_one(ingest_config_file, output_dir: str = OUTPUT_DIR, row_limit=None, force=False):
    source = f"./monarch_ingest/{ingest_config_file}"

    if not os.path.exists(source):
        raise ValueError(f"Transform source_config {source} does not exist")

    if ingest_output_exists(ingest_config_file, output_dir) and not force:
        return

    transform_source(
        source=source,
        output_dir=output_dir,
        output_format=OutputFormat.tsv,
        local_table=None,
        global_table=None,
        row_limit=row_limit,
    )

    if not ingest_output_exists(ingest_config_file, output_dir):
        raise ValueError(f"{ingest_config_file} did not produce the the expected output")

def ontology_transform(output_dir: str = OUTPUT_DIR, force=False):
    assert os.path.exists('data/monarch/monarch.json')

    edges = 'output/monarch_ontology_edges.tsv'
    nodes = 'output/monarch_ontology_nodes.tsv'

    # Since this is fairly slow, don't re-do it if the files exist unless forcing transforms
    # This shouldn't affect cloud builds, but will be handy for local runs
    if (
        not force
        and os.path.exists(edges)
        and os.path.exists(nodes)
        and os.path.getsize(edges) > 0
        and os.path.getsize(nodes)
    ):
        return

    kgx_transform(
        inputs=["data/monarch/monarch.json"],
        input_format="obojson",
        stream=False,
        output=f"{output_dir}/monarch_ontology",
        output_format="tsv",
    )

    if not file_exists(edges):
        raise ValueError("Ontology transform did not produce an edges file")
    if not file_exists(nodes):
        raise ValueError("Ontology transform did not produce a nodes file")

def merge_files(edge_files: List[str], node_files: List[str], file_root: str, output_dir: str = OUTPUT_DIR):

    os.makedirs(f"{output_dir}/merged", exist_ok=True)

    edge_dfs = []
    node_dfs = []
    for edge_file in edge_files:
        edge_dfs.append(
            pd.read_csv(
                edge_file, sep="\t", dtype="string", lineterminator="\n", index_col='id'
            )
        )
    for node_file in node_files:
        node_dfs.append(
            pd.read_csv(
                node_file, sep="\t", dtype="string", lineterminator="\n", index_col='id'
            )
        )

    edges = pd.concat(edge_dfs, axis=0)
    nodes = pd.concat(node_dfs, axis=0)

    # Clean up nodes, dropping duplicates and merging on the same ID, which causes some weirdness
    # with OMIM, where different categories use the same ID

    duplicate_nodes = nodes[nodes.index.duplicated(keep=False)]
    duplicate_nodes.to_csv(
        f"{output_dir}/merged/{file_root}-duplicate-nodes.tsv.gz", sep="\t"
    )

    nodes.drop_duplicates(inplace=True)
    nodes.index.name = 'id'
    nodes.fillna("None", inplace=True)
    column_agg = {x: ' '.join for x in nodes.columns if x != 'id'}
    nodes.groupby(['id'], as_index=True).agg(column_agg)

    nodes_path = f"{output_dir}/merged/{file_root}_nodes.tsv"
    nodes.to_csv(nodes_path, sep="\t")

    dangling_edges = edges[
        ~edges.subject.isin(nodes.index) | ~edges.object.isin(nodes.index)
    ]
    dangling_edges.to_csv(
        f"{output_dir}/merged/{file_root}-dangling-edges.tsv.gz", sep="\t"
    )

    edges = edges[edges.subject.isin(nodes.index) & edges.object.isin(nodes.index)]

    edges_path = f"{output_dir}/merged/{file_root}_edges.tsv"
    edges.to_csv(edges_path, sep="\t")

    tar = tarfile.open(f"{output_dir}/merged/{file_root}.tar.gz", "w:gz")
    tar.add(nodes_path)
    tar.add(edges_path)
    tar.close()

def run_ingests(output_dir: str = OUTPUT_DIR, row_limit: Optional[int] = None, force_transform=False):
    # TODO: download from data cache

    with open("ingests.yaml", "r") as stream:
        ingests = yaml.safe_load(stream)

    ontology_transform(output_dir=output_dir, force=force_transform)

    for ingest in ingests:
        task_name = f"transform {ingest['name']}"
        transform_one.with_options(name=task_name)(
            ingest['config'], force=force_transform, row_limit=row_limit
        )

    # TODO: if releasing/uploading, upload kgx files

    # Merge once without the ontology files
    edge_files = glob.glob(os.path.join(os.getcwd(), f"{output_dir}/*_edges.tsv"))
    node_files = glob.glob(os.path.join(os.getcwd(), f"{output_dir}/*_nodes.tsv"))

    merge_files(
        edge_files=edge_files,
        node_files=node_files,
        output_dir=output_dir,
        file_root="monarch-kg",
    )

    # TODO: if releasing/uploading, upload merged kgx
