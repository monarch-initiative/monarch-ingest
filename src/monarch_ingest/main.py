import sys
from typing import List, Optional
from pathlib import Path
import yaml
from kghub_downloader.download_utils import download_from_yaml
from monarch_ingest.cli_utils import (
    apply_closure,
    do_release,
    export_tsv,
    create_qc_reports,
    get_data_versions,
    get_pkg_versions,
    load_jsonl,
    load_neo4j_csv,
    load_sqlite,
    load_solr,
    merge_files,
    transform_one,
    transform_phenio,
    transform_all,
)
from monarch_ingest.utils.log_utils import get_logger

import typer


typer_app = typer.Typer()

OUTPUT_DIR = "output"


@typer_app.callback(invoke_without_command=True)
def callback(version: Optional[bool] = typer.Option(None, "--version", is_eager=True)):
    if version:
        from monarch_ingest import __version__

        typer.echo(f"monarch_ingest version: {__version__}")
        raise typer.Exit()


@typer_app.command()
def download(
    ingest: str = typer.Option(None, "--ingest", "-i", help="Run a single ingest (see download.yaml for a list)"),
    ingests: Optional[List[str]] = typer.Option(None, "--ingests", help="Which ingests to download data for"),
    ingest_file: Path = typer.Option(None, "--ingest_file", help="A yaml file which has a newline seperated list of ingests to perform."),
    all: bool = typer.Option(False, help="Download all ingest datasets"),
    write_metadata: bool = typer.Option(False, help="Write versions of ingests to metadata.yaml"),
):
    """Downloads data defined in download.yaml"""
    if(ingest==None and ingests==None and ingest_file==None and all==False):
        raise ValueError('Bad "ingest download" cli config. A flag must be provided for one of --ingest/-i, --ingests, --ingest_file, --all. None of these flags are provided.')
    #The following checks that *exactly* one of ingest, ingests, and ingest_file is set (i.e. has a value other than None).
    # If this isn't the case, we need to fail. 
    if(((ingest!=None) + (ingests!=None) + (ingest_file!=None) + (all!=False)) != 1):
        raise ValueError(f'Bad "ingest download" cli config. Exactly one flag can to be provided for the following options"--ingest/-i"'+\
                          f'"--ingests", "--ingest_file", "--all". We were provided "--ingest/-i"={ingest}, "--ingests"={ingests}, "--ingest_file"={ingest_file},"--all"={all}.')

    if(ingest): ingests=[ingest]
    if(ingest_file): ingests=yaml.safe_load(open(ingest_file))

    if ingests:
        download_from_yaml(
            yaml_file="src/monarch_ingest/download.yaml",
            output_dir=".",
            tags=ingests,
        )
    elif all:
        download_from_yaml(yaml_file="src/monarch_ingest/download.yaml", output_dir=".")
    if write_metadata:
        get_data_versions(output_dir="data")


@typer_app.command()
def transform(
    # data_dir: str = typer.Option('data', help='Path to data to ingest),
    output_dir: str = typer.Option(OUTPUT_DIR, "--output-dir", "-o", help="Directory to output data"),
    ingest: str = typer.Option(None, "--ingest", "-i", help="Run a single ingest (see ingests.yaml for a list)"),
    ingests: Optional[List[str]] = typer.Option(None, "--ingests", help="Which ingests to download data for"),
    ingest_file: Path = typer.Option(None, "--ingest_file", help="A yaml file which has a newline seperated list of ingests to perform."),
    phenio: bool = typer.Option(False, help="Run the phenio transform"),
    all: bool = typer.Option(False, "--all", "-a", help="Ingest all sources"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force ingest, even if output exists (on by default for single ingests)"
    ),
    rdf: bool = typer.Option(False, help="Output rdf files along with tsv"),
    verbose: Optional[bool] = typer.Option(
        None,
        "--debug/--quiet",
        "-d/-q",
        help="Use --quiet to suppress log output, --debug for verbose, including Koza logs",
    ),
    log: bool = typer.Option(False, "--log", "-l", help="Write DEBUG level logs to ./logs/ for each ingest"),
    row_limit: int = typer.Option(None, "--row-limit", "-n", help="Number of rows to process"),
    write_metadata: bool = typer.Option(False, help="Write data/package versions to output_dir/metadata.yaml"),
    # parallel: int = typer.Option(None, "--parallel", "-p", help="Utilize Dask to perform multiple ingests in parallel"),
):
    """Run Koza transformation on specified Monarch ingests"""
    if(ingest==None and ingests==None and ingest_file==None and all==False and phenio==False):
        raise ValueError('Bad "ingest transform" cli config. A flag must be provided for one of --ingest/-i, --ingests, --ingest_file, --all, or --phenio. None of these flags are provided.')
    #The following checks that *exactly* one of ingest, ingests, ingest_file, all, or phenio is set (i.e. has a value other than None).
    # If this isn't the case, we need to fail. 
    if(((ingest!=None) + (ingests!=None) + (ingest_file!=None) + (all!=False) + (phenio!=False)) != 1):
        raise ValueError(f'Bad "ingest transform" cli config. Exactly one flag can to be provided for the following options"--ingest/-i"'+\
                          f'"--ingests", "--ingest_file", "--phenio", "--all". We were provided "--ingest/-i"={ingest}, "--ingests"={ingests}, "--ingest_file"={ingest_file},"--all"={all},"--phenio"={phenio}.')

    if(ingest): ingests=[ingest]
    if(ingest_file): ingests=yaml.safe_load(open(ingest_file))

    if phenio:
        transform_phenio(output_dir=output_dir, force=force, verbose=verbose)
    elif ingests:
        for ingest in ingests:
            transform_one(
                ingest=ingest,
                output_dir=output_dir,
                row_limit=row_limit,
                rdf=rdf,
                force=True if force is None else force,
                verbose=verbose,
                log=log,
            )
    elif all:
        transform_all(
            output_dir=output_dir,
            row_limit=row_limit,
            rdf=rdf,
            force=force,
            verbose=verbose,
            log=log,
        )
    if write_metadata:
        get_pkg_versions(output_dir=output_dir)


@typer_app.command()
def merge(
    input_dir: str = typer.Option(
        f"{OUTPUT_DIR}/transform_output",
        help="Directory with nodes and edges to be merged",
    ),
    output_dir: str = typer.Option(f"{OUTPUT_DIR}", help="Directory to output data"),
    verbose: Optional[bool] = typer.Option(
        None, "--debug/--quiet", "-d/-q", help="Use --quiet to suppress log output, --debug for verbose"
    ),
    closure: bool = typer.Option(False, help="Apply closure to merged graph"),
    kg_name: str = typer.Option("monarch-kg", "--kg-name", "--kg_name", help="The name of the kg being produced. Merge artificat will be ultimately be stored in output/$KG_NAME.tar.gz"),
):
    """Merge nodes and edges into kg"""
    start_time = time.time()
    merge_files(input_dir=input_dir, output_dir=output_dir, verbose=verbose)
    merge_duration = time.time() - start_time

    # load qc_report.yaml from output_dir
    qc_report = yaml.safe_load(open(f"{output_dir}/qc_report.yaml"))
    if kg_name=="monarch-kg":
      expected_counts = yaml.safe_load(open(f"src/monarch_ingest/qc_expect.yaml"))
    else: 
      expected_counts = yaml.safe_load(open(f"src/monarch_ingest/{kg_name}_qc_expect.yaml"))

    error = False
    for type in ['nodes', 'edges']:
        counts = {item["name"]: item["total_number"] for item in qc_report[type]}
        for key in expected_counts[type]["provided_by"]:
            expected = expected_counts[type]["provided_by"][key]["min"]
            way_less_than_expected = expected * 0.7
            if key not in counts:
                error = True
                print(f"ERROR: {type} {key} not found in qc_report.yaml")
            else:
                if counts[key] < expected and counts[key] > way_less_than_expected:
                    print(f"WARNING: expected {key} to have {expected} {type}, only found {counts[key]}")
                elif counts[key] < expected * 0.7:
                    print(f"ERROR: expected {key} to have {expected} {type}, only found {counts[key]}")
                    error = True

    closure_duration = None
    if closure:
        closure_start = time.time()
        apply_closure()
        closure_duration = time.time() - closure_start

    print(f"Merge step took {merge_duration:.2f} seconds.")
    if closure_duration is not None:
        print(f"Closure step took {closure_duration:.2f} seconds.")

    if error:
        sys.exit(1)


@typer_app.command()
def closure():
    apply_closure()


@typer_app.command()
def jsonl():
    load_jsonl()

@typer_app.command()
def neo4j_csv():
    load_neo4j_csv()    


@typer_app.command()
def sqlite():
    load_sqlite()


@typer_app.command()
def solr():
    load_solr()


@typer_app.command()
def export():
    export_tsv()

@typer_app.command()
def report():
    """Run Koza QC on specified Monarch ingests"""
    create_qc_reports()


@typer_app.command()
def release(
    dir: str = typer.Option(f"{OUTPUT_DIR}", help="Directory with kg to be released"),
    kghub: bool = typer.Option(False, help="Also release to kghub S3 bucket"),
):
    """Copy data to Monarch GCP data buckets"""
    do_release(dir, kghub)


#######################################################

if __name__ == "__main__":
    typer_app()
