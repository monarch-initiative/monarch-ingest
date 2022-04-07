from prefect import flow, task
from prefect.task_runners import DaskTaskRunner, RayTaskRunner, SequentialTaskRunner
from koza.cli_runner import transform_source
from koza.model.config.source_config import OutputFormat
import yaml
import typer
from typing import Optional, List
import glob
import os
import pandas as pd

@task()
def transform(ingest_config, row_limit=None):
    source = f"./monarch_ingest/{ingest_config}"

    if not os.path.exists(source):
        raise ValueError(f"Transform source_config {source} does not exist")

    transform_source(
        source=source,
        output_dir="output",
        output_format=OutputFormat.tsv,
        local_table=None,
        global_table=None,
        row_limit=row_limit
    )


@task()
def merge(edge_files: List[str], node_files: List[str]):
    edge_dfs = []
    node_dfs = []
    for edge_file in edge_files:
        edge_dfs.append(pd.read_csv(edge_file, sep="\t", dtype="string", lineterminator="\n"))
    for node_file in node_files:
        node_dfs.append(pd.read_csv(node_file, sep="\t", dtype="string", lineterminator="\n"))

    edges = pd.concat(edge_dfs, axis=0)
    nodes = pd.concat(node_dfs, axis=0)

    # todo: log and remove edges with dangling subjects & objects

    edges.to_csv("monarch-kg_edges.tsv", sep="\t")
    nodes.to_csv("monarch-kg_nodes.tsv", sep="\t")


# Commenting out the DaskTaskRunner because the cluster arrangement is hitting singleton problems with Koza
# @flow(task_runner=DaskTaskRunner(cluster_kwargs={"memory_limit": "6 GiB", "n_workers": 1}))
@flow(task_runner=SequentialTaskRunner)
def run_ingests(row_limit: Optional[int] = None):

    # todo: download from data cache

    with open("ingests.yaml", "r") as stream:
        ingests = yaml.safe_load(stream)

    for ingest in ingests:
        print(ingest)
        task_name = f"transform {ingest['name']}"
        transform.with_options(name=task_name)(ingest['config'], row_limit)

    # todo: if releasing/uploading, upload kgx files

    edge_files = glob.glob(os.path.join(os.getcwd(), "output/*edges.tsv"))
    node_files = glob.glob(os.path.join(os.getcwd(), "output/*nodes.tsv"))

    merge(edge_files=edge_files, node_files=node_files)

    # todo: if releasing/uploading, upload merged kgx


if __name__ == "__main__":
    typer.run(run_ingests)
