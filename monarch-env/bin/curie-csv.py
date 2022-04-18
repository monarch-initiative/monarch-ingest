#!/mnt/d/dev/tislab/monarch-ingest/monarch-env/bin/python

from prefixcommons import CsvTransformer
from prefixcommons.curie_util import read_biocontext
import click

@click.command()
@click.option("--cmap", "-m", multiple=True)
@click.option("--contract/--expand", default=False)
@click.option("--output", "-o")
@click.argument("input")
def convert(input,output,contract,cmap):
    cmaps = [read_biocontext(x) for x in cmap]
    if cmaps == []:
        cmaps = None
    t = CsvTransformer(cmaps=cmaps, contract=contract)
    t.transform(input, output)
    

if __name__ == "__main__":
    convert()
