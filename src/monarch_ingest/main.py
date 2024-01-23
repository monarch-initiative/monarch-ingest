from typing import List, Optional

from kghub_downloader.download_utils import download_from_yaml
from monarch_ingest.cli_utils import (
    apply_closure, 
    do_release,
    export_tsv,
    load_jsonl,
    load_sqlite, 
    load_solr, 
    merge_files, 
    transform_one, 
    transform_phenio, 
    transform_all, 
)

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
    ingests: Optional[List[str]] = typer.Option(None,  help="Which ingests to download data for"),
    all: bool = typer.Option(False, help="Download all ingest datasets"),
    write_versions: bool = typer.Option(False, help="Write versions of ingests to versions.yaml")
    ):
    """Downloads data defined in download.yaml"""

    if ingests:
        download_from_yaml(
            yaml_file='src/monarch_ingest/download.yaml',
            output_dir='.',
            tags=ingests,
        )
    elif all:
        download_from_yaml(
            yaml_file='src/monarch_ingest/download.yaml',
            output_dir='.'
        )

    if write_versions:
        # TODO: 
        # - Find a way to get versions of other data sources
        # - May need beautifulsoup to scrape some web pages
        # - Split data and packages into separate sections
        import requests as r
        from importlib.metadata import version

        packages = {}
        data = {} 
        
        # get biolink model version
        packages["biolink"] = version("biolink-model")
        packages["monarch-ingest"] = version("monarch-ingest")
        
        # github api query for mondo, phenio, hpo versions
        data["phenio"] = r.get("https://api.github.com/repos/monarch-initiative/phenio/releases").json()[0]["tag_name"]
        data["hpo"] = r.get("https://api.github.com/repos/obophenotype/human-phenotype-ontology/releases").json()[0]["tag_name"]
        data["mondo"] = r.get("https://api.github.com/repos/monarch-initiative/mondo/releases").json()[0]["tag_name"]
        
        # get alliance version from alliance api endpoint
        data["alliance"] = r.get("https://fms.alliancegenome.org/api/releaseversion/current").json()["releaseVersion"]

        # zfin -> daily build, no version (or use beautifulsoup)

        # write to versions.yaml
        with open("versions.yaml", "w") as f:
            f.write("packages:\n")
            for package, version in packages.items():
                f.write(f"  {package}: {version}\n")
            f.write("data:\n")
            for data_source, version in data.items():
                f.write(f"  {data_source}: {version}\n")


@typer_app.command()
def transform(
    # data_dir: str = typer.Option('data', help='Path to data to ingest),
    output_dir: str = typer.Option(OUTPUT_DIR, "--output-dir", "-o", help="Directory to output data"),
    ingest: str = typer.Option(None, "--ingest", "-i", help="Run a single ingest (see ingests.yaml for a list)"),
    phenio: bool = typer.Option(False, help="Run the phenio transform"),
    all: bool = typer.Option(False, "--all", "-a", help="Ingest all sources"),
    force: bool = typer.Option(False, "--force", "-f", help="Force ingest, even if output exists (on by default for single ingests)"),
    rdf: bool = typer.Option(False, help="Output rdf files along with tsv"),
    verbose: Optional[bool] = typer.Option(None, "--debug/--quiet", "-d/-q", help="Use --quiet to suppress log output, --debug for verbose, including Koza logs"),
    log: bool = typer.Option(False, "--log", "-l", help="Write DEBUG level logs to ./logs/ for each ingest"),
    row_limit: int = typer.Option(None, "--row-limit", "-n", help="Number of rows to process"),
    # parallel: int = typer.Option(None, "--parallel", "-p", help="Utilize Dask to perform multiple ingests in parallel"),
):
    """Run Koza transformation on specified Monarch ingests"""

    if phenio:
        transform_phenio(
            output_dir=output_dir,
            force=force,
            verbose=verbose
        )
    elif ingest:
        transform_one(
            ingest = ingest,
            output_dir = output_dir,
            row_limit = row_limit,
            rdf = rdf,
            force = True if force is None else force,
            verbose = verbose,
            log = log,
        )
    elif all:
        transform_all(
            output_dir = output_dir,
            row_limit = row_limit,
            rdf = rdf,
            force = force,
            verbose=verbose,
            log = log,
        )


@typer_app.command()
def merge(
    input_dir: str = typer.Option(f"{OUTPUT_DIR}/transform_output", help="Directory with nodes and edges to be merged",),
    output_dir: str = typer.Option(f"{OUTPUT_DIR}", help="Directory to output data"),
    verbose: Optional[bool] = typer.Option(None, "--debug/--quiet", "-d/-q", help="Use --quiet to suppress log output, --debug for verbose"),
    ):
    """Merge nodes and edges into kg"""
    merge_files(input_dir=input_dir, output_dir=output_dir, verbose=verbose)


@typer_app.command()
def closure():
    apply_closure()

@typer_app.command()
def jsonl():
    load_jsonl()

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
def release(
    dir: str = typer.Option(f"{OUTPUT_DIR}", help="Directory with kg to be released"),
    kghub: bool = typer.Option(False, help="Also release to kghub S3 bucket")
    ):
    """Copy data to Monarch GCP data buckets"""
    do_release(dir, kghub)


#######################################################

if __name__ == "__main__":
    typer_app()
