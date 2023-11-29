import uuid
from typing import Optional, Tuple

from koza.cli_runner import get_koza_app
from monarch_ingest.ingests.dictybase.utils import parse_gene_id, parse_phenotypes

from biolink.pydanticmodel_v2 import GeneToPhenotypicFeatureAssociation

koza_app = get_koza_app("dictybase_gene_to_phenotype")

while (row := koza_app.get_row()) is not None:

    phenotype_names_to_ids = koza_app.get_map("dictybase_phenotype_names_to_ids")

    gene_identifier = ['dictyBase:' + gene_id for gene_id in row['DDB_G_ID'].split("|")]

    if len(gene_identifier) == 1:

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
                aggregator_knowledge_source=["infores:monarchinitiative"],
                primary_knowledge_source="infores:dictybase"
            )

            koza_app.write(association)
