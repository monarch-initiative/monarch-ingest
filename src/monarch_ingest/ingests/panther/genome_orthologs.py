"""
Ingest of Reference Genome Orthologs from Panther
"""

import uuid

from koza.cli_utils import get_koza_app

from biolink_model.datamodel.pydanticmodel_v2 import GeneToGeneHomologyAssociation, KnowledgeLevelEnum, AgentTypeEnum

from monarch_ingest.ingests.panther.orthology_utils import parse_gene, ncbitaxon_catalog


koza_app = get_koza_app("panther_genome_orthologs")

while (row := koza_app.get_row()) is not None:

    if row['Gene'].split("|")[0] in ncbitaxon_catalog and row['Ortholog'].split("|")[0] in ncbitaxon_catalog:
        try:
            # TODO: we don't current capture the taxon of the subject gene
            #       nor the object ortholog. Maybe as a qualifier in Biolink 3.0?

            species_and_gene_id = parse_gene(row['Gene'])

            if species_and_gene_id is None:
                continue

            # unpack the species and gene id
            gene_ncbitaxon, gene_id = species_and_gene_id

            species_and_ortholog_id = parse_gene(row['Ortholog'])

            # unpack the orthogous gene id and its species
            if species_and_ortholog_id is None:
                continue

            ortholog_ncbitaxon, ortholog_id = species_and_ortholog_id

            # TODO: how do I discriminate between LDO and O? I don't care for now??
            #       However, this may result in KGX record duplication?
            # ortholog_type = row["Type of ortholog"]
            predicate = "biolink:orthologous_to"

            # Instantiate the instance of Gene-to-Gene Homology Association
            panther_ortholog_id = row["Panther Ortholog ID"]
            association = GeneToGeneHomologyAssociation(
                id=f"uuid:{str(uuid.uuid1())}",
                subject=gene_id,
                object=ortholog_id,
                predicate=predicate,
                has_evidence=[f"PANTHER.FAMILY:{panther_ortholog_id}"],
                aggregator_knowledge_source=["infores:monarchinitiative"],
                primary_knowledge_source="infores:panther",
                knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
                agent_type=AgentTypeEnum.not_provided,
            )

            # Write the captured Association out
            koza_app.write(association)

        except RuntimeError:
            # Skip the row - not of interest or error
            # logger.debug(f"{str(rte)} in data row:\n\t'{str(row)}'")
            pass
