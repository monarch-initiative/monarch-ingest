from koza.cli_runner import koza_app
from source_translation import source_map

from model.biolink import Gene

source_name = "alliance_gene"

row = koza_app.get_row(source_name)
# curie prefix as source?
source = source_map[row["basicGeneticEntity"]["primaryId"].split(":")[0]]

if "name" not in row.keys():
    row["name"] = row["symbol"]

gene = Gene(
    id=row["basicGeneticEntity"]["primaryId"],
    symbol=row["symbol"],
    name=row["name"],
    type=row["soTermId"],
    in_taxon=[row["basicGeneticEntity"]["taxonId"]],
    source=source,
)

if row["basicGeneticEntity"]["crossReferences"]:
    gene.xrefs = [
        koza_app.curie_cleaner.clean(xref["id"])
        for xref in row["basicGeneticEntity"]["crossReferences"]
    ]
if "synonyms" in row["basicGeneticEntity"].keys():
    gene.synonym = row["basicGeneticEntity"]["synonyms"]

koza_app.write(gene)
