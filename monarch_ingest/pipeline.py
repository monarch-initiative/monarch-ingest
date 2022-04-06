from prefect import flow, task
from prefect.task_runners import DaskTaskRunner
from koza.cli_runner import transform_source
from koza.model.config.source_config import OutputFormat
import yaml
import typer
from typing import Optional

@task
def transform(ingest_config, row_limit=None):
    transform_source(
        source=f"./monarch_ingest/{ingest_config}",
        output_dir="output",
        output_format=OutputFormat.tsv,
        local_table=None,
        global_table=None,
        row_limit=row_limit
    )


@flow(task_runner=DaskTaskRunner())
def run_ingests(rows: Optional[int] = None):
    with open("ingests.yaml", "r") as stream:
        ingests = yaml.safe_load(stream)

    for ingest in ingests:
        print(ingest)
        transform(ingest['config'], rows)


if __name__ == "__main__":
    typer.run(run_ingests)
