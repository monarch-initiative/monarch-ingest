import uuid
from koza.cli_runner import get_koza_app
from biolink.pydanticmodel import PairwiseGeneToGeneInteraction
from biogrid_util import get_gene_id, get_evidence, get_publication_ids

koza_app = get_koza_app("biogrid")

while (row := koza_app.get_row()) is not None:

    gid_a = get_gene_id(row['ID Interactor A'])
    gid_b = get_gene_id(row['ID Interactor B'])

    evidence = get_evidence(row['Interaction Detection Method'])

    publications = get_publication_ids(row['Publication Identifiers'])

    association = PairwiseGeneToGeneInteraction(
        id="uuid:" + str(uuid.uuid1()),
        subject=gid_a,
        predicate="biolink:interacts_with",
        object=gid_b,
        has_evidence=evidence,
        publications=publications,
        primary_knowledge_source="infores:biogrid",
        aggregator_knowledge_source=["infores:monarchinitiative"]
    )

    koza_app.write(association)
