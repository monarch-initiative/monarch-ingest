"""
Ingest of Reference Genome Orthologs from Xenbase
"""
import logging
import uuid

from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import GeneToGeneHomologyAssociation

logger = logging.getLogger(__name__)

koza_app = get_koza_app("xenbase_non_entrez_orthologs")

while (row := koza_app.get_row()) is not None:

    try:
        gene_id = row['Xenbase']

        predicate = "biolink:orthologous_to"

        omim_id = row['OMIM']
        mgi_id = row['MGI']
        zfin_id = row['ZFIN']

        # Instantiate the instance of Gene-to-Gene Homology Associations for each ortholog
        if omim_id:
            association = GeneToGeneHomologyAssociation(
                id=f"uuid:{str(uuid.uuid1())}",
                subject=f"Xenbase:{gene_id}",
                predicate=predicate,
                object=f"OMIM:{omim_id}",
                aggregator_knowledge_source=["infores:monarchinitiative"],
                primary_knowledge_source="infores:xenbase"
            )

            # Write the captured Association out
            koza_app.write(association)

        if mgi_id:
            association = GeneToGeneHomologyAssociation(
                id=f"uuid:{str(uuid.uuid1())}",
                subject=f"Xenbase:{gene_id}",
                predicate=predicate,
                object=f"MGI:{mgi_id}",
                aggregator_knowledge_source=["infores:monarchinitiative"],
                primary_knowledge_source="infores:xenbase"
            )

            # Write the captured Association out
            koza_app.write(association)

        if zfin_id:
            association = GeneToGeneHomologyAssociation(
                id=f"uuid:{str(uuid.uuid1())}",
                subject=f"Xenbase:{gene_id}",
                predicate=predicate,
                object=f"ZFIN:{zfin_id}",
                aggregator_knowledge_source=["infores:monarchinitiative"],
                primary_knowledge_source="infores:xenbase"
            )

            # Write the captured Association out
            koza_app.write(association)

    except (RuntimeError, AssertionError) as rte:
        logger.debug(f"{str(rte)} in data row:\n\t'{str(row)}'")
