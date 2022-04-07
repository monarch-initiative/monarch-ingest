from prefect import flow, task
from prefect.task_runners import DaskTaskRunner
from koza.cli_runner import transform_source
from koza.model.config.source_config import OutputFormat
import yaml
import typer
from typing import Optional
from os import path


@task()
def transform(ingest_config, row_limit=None):
    source = f"./monarch_ingest/{ingest_config}"

    if not path.exists(source):
        raise ValueError(f"Transform source_config {source} does not exist")

    transform_source(
        source=source,
        output_dir="output",
        output_format=OutputFormat.tsv,
        local_table=None,
        global_table=None,
        row_limit=row_limit
    )


@flow(task_runner=DaskTaskRunner(cluster_kwargs={"memory_limit": "6 GiB"}))
def run_ingests(row_limit: Optional[int] = None):
    with open("ingests.yaml", "r") as stream:
        ingests = yaml.safe_load(stream)

    for ingest in ingests:
        print(ingest)
        task_name = f"transform {ingest['name']}"
        transform.with_options(name=task_name)(ingest['config'], row_limit)


if __name__ == "__main__":
    typer.run(run_ingests)
