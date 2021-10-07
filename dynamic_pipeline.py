import os
from pathlib import Path
from dagster import ModeDefinition, \
    multiprocess_executor, fs_io_manager, pipeline, solid, \
    DynamicOutputDefinition, Field, file_relative_path, DynamicOutput
from koza.cli_runner import transform_source
from koza.model.config.source_config import OutputFormat

mode_defs = [
    ModeDefinition(
        resource_defs={"io_manager": fs_io_manager},
        executor_defs=[multiprocess_executor],
    )
]



@solid
def transform(ingest):
    source = str(ingest.parent.stem)
    source_file = str(ingest.name)
    transform_source(f"./monarch_ingest/{source}/{source_file}",
                     "output", OutputFormat.tsv, "./monarch_ingest/translation_table.yaml", None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them


@solid(
    config_schema={
        "path": Field(str, default_value=file_relative_path(__file__, "monarch_ingest"))
    },
    output_defs=[DynamicOutputDefinition(Path)],
)
def ingests(context):
    path = Path(context.solid_config["path"])
    ingest_dirs = [dir.parent for dir in path.rglob("metadata.yaml")]

    for ingest_dir in ingest_dirs:
        source_ingests = [ingest_file for ingest_file in list(ingest_dir.rglob("*.yaml"))
                          if not ingest_file.match("metadata.yaml")]
        for ingest in source_ingests:
            mapping_key = ingest.parent.stem + "_" + ingest.stem
            yield DynamicOutput(ingest, mapping_key=mapping_key)

@solid
def merge(placeholder_input):
    os.system("kgx merge --merge-config merge.yaml --processes 4")


@pipeline(mode_defs=mode_defs)
def monarch_ingest_pipeline():
    x = ingests().map(transform)
    merge(x.collect())


