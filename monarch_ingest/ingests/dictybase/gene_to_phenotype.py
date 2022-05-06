import uuid

from biolink_model_pydantic.model import (
    Gene,
    GeneToPhenotypicFeatureAssociation,
    PhenotypicFeature,
    Predicate,
)
from koza.cli_runner import koza_app

source_name = "dictybase_gene_to_phenotype"

#   - 'Systematic Name'
#   - 'Strain Descriptor'
#   - 'Associated gene(s)' - may be locus identifiers or gene symbols
#   - 'Phenotypes'
row = koza_app.get_row(source_name)
gene_ids = koza_app.get_map("dictybase_gene_to_symbol")

genes: str = row['Associated gene(s)']
if genes and len(genes) == 1:
    gene_id = genes
    gene = Gene(id="dictyBase:" + row["Gene systematic ID"], source="infores:dictybase")

    phenotypes = row["Phenotypes"]
    phenotype = PhenotypicFeature(id=row["FYPO ID"], source="infores:dictybase")
    association = GeneToPhenotypicFeatureAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene.id,
        predicate=Predicate.has_phenotype,
        object=phenotype.id,
        relation=koza_app.translation_table.resolve_term("has phenotype"),
        source="infores:dictybase"
    )

    koza_app.write(association)
