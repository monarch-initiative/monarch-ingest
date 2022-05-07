import uuid

from biolink_model_pydantic.model import (
    GeneToPhenotypicFeatureAssociation,
    Predicate,
)
from koza.cli_runner import koza_app
from monarch_ingest.ingests.dictybase.utils import parse_gene_id, parse_phenotypes

source_name = "dictybase_gene_to_phenotype"

row = koza_app.get_row(source_name)

gene_names_to_ids = koza_app.get_map("dictybase_gene_names_to_ids")
phenotype_names_to_ids = koza_app.get_map("dictybase_phenotype_names_to_ids")

gene_id: str = parse_gene_id(row, gene_names_to_ids)
if gene_id:

    # Parse out list of phenotypes...
    phenotypes = parse_phenotypes(row, phenotype_names_to_ids)

    for phenotype_id in phenotypes:
        # Create one S-P-O statement per phenotype
        # TODO: how do we capture the 'Strain Descriptor' (genotype) context of
        #       Dictylostelium via which a (mutant) gene (allele) is tied to its phenotype?
        association = GeneToPhenotypicFeatureAssociation(
            id="uuid:" + str(uuid.uuid1()),
            subject=gene_id,
            predicate=Predicate.has_phenotype,
            object=phenotype_id,
            relation=koza_app.translation_table.resolve_term("has phenotype"),
            source="infores:dictybase"
        )

        koza_app.write(association)
