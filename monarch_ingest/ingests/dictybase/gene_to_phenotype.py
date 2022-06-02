import uuid
from typing import Optional, Tuple

from model.biolink import GeneToPhenotypicFeatureAssociation
from koza.cli_runner import koza_app
from monarch_ingest.ingests.dictybase.utils import parse_gene_id, parse_phenotypes

source_name = "dictybase_gene_to_phenotype"

row = koza_app.get_row(source_name)

gene_names_to_ids = koza_app.get_map("dictybase_gene_names_to_ids")
phenotype_names_to_ids = koza_app.get_map("dictybase_phenotype_names_to_ids")

gene_identifier: Optional[Tuple[str, str]] = parse_gene_id(row, gene_names_to_ids)
if gene_identifier:

    # Parse out list of phenotypes...
    phenotypes = parse_phenotypes(row, phenotype_names_to_ids)

    for phenotype_id in phenotypes:
        # Create one S-P-O statement per phenotype
        # TODO: how do we capture the 'Strain Descriptor' (genotype) context of
        #       Dictylostelium via which a (mutant) gene (allele) is tied to its phenotype?
        association = GeneToPhenotypicFeatureAssociation(
            id="uuid:" + str(uuid.uuid1()),
            subject=gene_identifier[0],  # gene[0] is the resolved gene ID
            predicate='biolink:has_phenotype',
            object=phenotype_id,
            source="infores:dictybase"
        )

        koza_app.write(association)