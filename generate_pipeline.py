from jinja2 import Template
from pathlib import Path

ingests = []

ingest_dirs = [dir.parent for dir in Path("./monarch_ingest").rglob("metadata.yaml")]

for ingest_dir in ingest_dirs:
    source_ingests = [ingest_file for ingest_file in list(ingest_dir.rglob("*.yaml"))
                      if not ingest_file.match("metadata.yaml")]
    for ingest in source_ingests:
        ingests.append({
            'source':str(ingest.parent.stem),
            'source_file':str(ingest.name),
            'source_file_stem': str(ingest.stem),
            'ingest_method': 'ingest_' + str(ingest.parent.stem) + '_' + str(ingest.stem) + '()'
        })

ingest_methods = ', '.join([ingest['ingest_method'] for ingest in ingests])


template = """
import os
from dagster import ModeDefinition, InputDefinition, Nothing, default_executors, multiprocess_executor, fs_io_manager, pipeline, solid, composite_solid
from koza.cli_runner import transform_source

mode_defs = [
    ModeDefinition(
        resource_defs={"io_manager": fs_io_manager},
        executor_defs=[multiprocess_executor],
    )
]

ingest_home = '/Users/kschaper/Documents/Monarch/monarch-ingest/'

{% for ingest in ingests %}

@solid
def {{ingest.ingest_method}}:
    transform_source(ingest_home + "monarch_ingest/{{ ingest.source }}/{{ ingest.source_file }}",
                     "output", "tsv", ingest_home + "monarch_ingest/translation_table.yaml", None)
    return 1 # This is a hack, we don't really have natural return values, but Dagster wants them 

{% endfor %}

@solid
def merge(placeholder_input):
    os.system("kgx merge --merge-config merge.yaml --processes 4")

@pipeline(mode_defs=mode_defs)
def monarch_ingest_pipeline():    
    merge([{{ingest_methods}}])

"""


print(Template(template).render(ingests=ingests, ingest_methods=ingest_methods))
