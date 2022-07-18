import logging
import uuid

from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import InformationContentEntityToNamedThingAssociation

LOG = logging.getLogger(__name__)

koza_app = get_koza_app("xenbase_publication_to_gene")

row = koza_app.get_row()
genepage2gene = koza_app.get_map("genepage-2-gene")

entities = []

gene_pages = row["gene_pages"]

publication_id = "PMID:" + row["pmid"]

for gene_page in gene_pages.split(","):

    gene_page_id = gene_page.split(" ")[0]
    try:
        gene_ids = map(
            lambda id: f"Xenbase:{id}", list(genepage2gene[gene_page_id].values())
        )
    except KeyError:
        LOG.debug(f"Could not locate genepage_id: {gene_page_id} in row {row}")
        continue

    for gene_id in gene_ids:

        association = InformationContentEntityToNamedThingAssociation(
            id="uuid:" + str(uuid.uuid1()),
            subject=gene_id,
            predicate="biolink:mentions",
            object=publication_id,
            aggregator_knowledge_source=["infores:monarchinitiative"],
            primary_knowledge_source="infores:xenbase"
        )

        entities.append(association)

koza_app.write(*entities)
