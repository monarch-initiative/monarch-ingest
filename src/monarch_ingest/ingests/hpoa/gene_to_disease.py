from biolink.pydanticmodel import GeneToDiseaseAssociation
from koza.cli_runner import get_koza_app

from monarch_ingest.constants import INFORES_MONARCHINITIATIVE
from monarch_ingest.ingests.hpoa.hpoa_utils import get_knowledge_sources, get_predicate

koza_app = get_koza_app("hpoa_gene_to_disease")


while (row := koza_app.get_row()) is not None:
    gene_id = row["ncbi_gene_id"]
    disease_id = row["disease_id"]

    predicate = get_predicate(row["association_type"])

    primary_knowledge_source, aggregator_knowledge_source = get_knowledge_sources(row["source"], INFORES_MONARCHINITIATIVE)

    association = GeneToDiseaseAssociation(
        subject=gene_id,
        predicate=predicate,
        object=disease_id,
        primary_knowledge_source=primary_knowledge_source,
        aggregator_knowledge_source=aggregator_knowledge_source
    )

    koza_app.write(association)
