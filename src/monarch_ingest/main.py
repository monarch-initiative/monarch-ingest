import sys
import time
from typing import List, Optional
from pathlib import Path
import yaml

from monarch_ingest.utils.log_utils import get_logger
from monarch_ingest.utils.ingest_utils import validate_qc_counts

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
    ingest_file: Path = typer.Option(
        None, "--ingest_file", help="A yaml file which has a newline seperated list of ingests to perform."
    ),
    all: bool = typer.Option(True, help="Download all ingest datasets"),
    write_metadata: bool = typer.Option(False, help="Write versions of ingests to metadata.yaml"),
):
    """Downloads data defined in download.yaml and runs post-download processing"""
    from kghub_downloader.download_utils import download_from_yaml
    from monarch_ingest.cli_utils import get_data_versions

    if ingest:
        ingests = [ingest]
    if ingest_file:
        ingests = yaml.safe_load(open(ingest_file))

    if ingests:
        download_from_yaml(
            yaml_file="src/monarch_ingest/download.yaml",
            output_dir=".",
            tags=ingests,
        )
    else:
        download_from_yaml(yaml_file="src/monarch_ingest/download.yaml", output_dir=".")

    # Run post-download processing (prefix repairs, phenio filtering, etc.)
    after_download_script = Path("scripts/after_download.sh")
    if after_download_script.exists():
        import subprocess
        logger = get_logger()
        logger.info("Running post-download processing...")
        result = subprocess.run(["sh", str(after_download_script)], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"after_download.sh failed: {result.stderr}")
        else:
            logger.info("Post-download processing complete.")

    if write_metadata:
        get_data_versions(output_dir="data")


@typer_app.command()
def transform(
    # data_dir: str = typer.Option('data', help='Path to data to ingest),
    output_dir: str = typer.Option(OUTPUT_DIR, "--output-dir", "-o", help="Directory to output data"),
    ingest: str = typer.Option(None, "--ingest", "-i", help="Run a single ingest (see ingests.yaml for a list)"),
    ingests: Optional[List[str]] = typer.Option(None, "--ingests", help="Which ingests to download data for"),
    ingest_file: Path = typer.Option(
        None, "--ingest_file", help="A yaml file which has a newline seperated list of ingests to perform."
    ),
    phenio: bool = typer.Option(False, help="Run the phenio transform"),
    all: bool = typer.Option(False, "--all", "-a", help="Ingest all sources"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force ingest, even if output exists (on by default for single ingests)"
    ),

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
    from monarch_ingest.cli_utils import transform_one, transform_phenio, transform_all, get_pkg_versions

    if ingest == None and ingests == None and ingest_file == None and all == False and phenio == False:
        raise ValueError(
            'Bad "ingest transform" cli config. A flag must be provided for one of --ingest/-i, --ingests, --ingest_file, --all, or --phenio. None of these flags are provided.'
        )
    # The following checks that *exactly* one of ingest, ingests, ingest_file, all, or phenio is set (i.e. has a value other than None).
    # If this isn't the case, we need to fail.
    if ((ingest != None) + (ingests != None) + (ingest_file != None) + (all != False) + (phenio != False)) != 1:
        raise ValueError(
            f'Bad "ingest transform" cli config. Exactly one flag can to be provided for the following options"--ingest/-i"'
            + f'"--ingests", "--ingest_file", "--phenio", "--all". We were provided "--ingest/-i"={ingest}, "--ingests"={ingests}, "--ingest_file"={ingest_file},"--all"={all},"--phenio"={phenio}.'
        )

    if ingest:
        ingests = [ingest]
    if ingest_file:
        ingests = yaml.safe_load(open(ingest_file))

    if phenio:
        transform_phenio(output_dir=output_dir, force=force, verbose=verbose)
    elif ingests:
        for ingest in ingests:
            transform_one(
                ingest=ingest,
                output_dir=output_dir,
                row_limit=row_limit,
                force=True if force is None else force,
                verbose=verbose,
                log=log,
            )
    elif all:
        transform_all(
            output_dir=output_dir,
            row_limit=row_limit,
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
    kg_name: str = typer.Option(
        "monarch-kg",
        "--kg-name",
        "--kg_name",
        help="The name of the kg being produced. Merge artificat will be ultimately be stored in output/$KG_NAME.tar.gz",
    ),
):
    """Merge nodes and edges into kg"""
    from monarch_ingest.cli_utils import apply_closure, merge_files

    logger = get_logger(None, verbose)
    start_time = time.time()
    merge_files(name=kg_name, input_dir=input_dir, output_dir=output_dir, verbose=verbose)
    merge_duration = time.time() - start_time

    # load qc_report.yaml from output_dir
    qc_report = yaml.safe_load(open(f"{output_dir}/qc_report.yaml"))
    if kg_name == "monarch-kg":
        expected_counts = yaml.safe_load(open(f"src/monarch_ingest/qc_expect.yaml"))
    else:
        expected_counts = yaml.safe_load(open(f"src/monarch_ingest/{kg_name}_qc_expect.yaml"))

    error = validate_qc_counts(qc_report, expected_counts, logger=logger)

    closure_duration = None
    if closure:
        closure_start = time.time()
        apply_closure()
        closure_duration = time.time() - closure_start

    logger.info(f"Merge step took {merge_duration:.2f} seconds")
    if closure_duration is not None:
        logger.info(f"Closure step took {closure_duration:.2f} seconds")

    if error:
        sys.exit(1)


@typer_app.command()
def closure():
    from monarch_ingest.cli_utils import apply_closure

    apply_closure()


@typer_app.command()
def jsonl():
    from monarch_ingest.cli_utils import load_jsonl

    load_jsonl()


@typer_app.command()
def neo4j_csv():
    from monarch_ingest.cli_utils import load_neo4j_csv

    load_neo4j_csv()


@typer_app.command()
def sqlite():
    from monarch_ingest.cli_utils import load_sqlite

    load_sqlite()


@typer_app.command()
def solr():
    from monarch_ingest.cli_utils import load_solr

    load_solr()


@typer_app.command()
def export():
    from monarch_ingest.cli_utils import export_tsv

    export_tsv()


@typer_app.command()
def report():
    """Run Koza QC on specified Monarch ingests"""
    from monarch_ingest.cli_utils import create_qc_reports

    create_qc_reports()


@typer_app.command()
def graph_stats(
    input_db: str = typer.Option(
        f"{OUTPUT_DIR}/monarch-kg.duckdb",
        "--input-db",
        "-i",
        help="Path to input DuckDB database",
    ),
    output_file: str = typer.Option(
        f"{OUTPUT_DIR}/merged_graph_stats.yaml",
        "--output",
        "-o",
        help="Output YAML file path",
    ),
    backend: str = typer.Option(
        "koza",
        "--backend",
        "-b",
        help="Backend to use: 'koza' (new) or 'kgx' (legacy)",
    ),
):
    """Generate graph statistics from merged KG database"""
    from monarch_ingest.cli_utils import generate_graph_stats

    generate_graph_stats(
        input_db=input_db,
        output_file=output_file,
        backend=backend,
    )


@typer_app.command()
def release(
    dir: str = typer.Option(f"{OUTPUT_DIR}", help="Directory with kg to be released"),
    kghub: bool = typer.Option(False, help="Also release to kghub S3 bucket"),
):
    """Copy data to Monarch GCP data buckets"""
    from monarch_ingest.cli_utils import do_release

    do_release(dir, kghub)


#######################################################

if __name__ == "__main__":
    typer_app()
