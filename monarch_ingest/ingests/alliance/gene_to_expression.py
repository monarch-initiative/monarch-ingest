import logging
import uuid

from koza.cli_runner import koza_app
from source_translation import source_map

from biolink.pydantic.model import GeneToExpressionSiteAssociation

from monarch_ingest.ingests.alliance.utils import get_data

logger = logging.getLogger(__name__)

source_name = "alliance_gene_to_expression"

row = koza_app.get_row(source_name)

EXPRESSED_IN_RELATION = koza_app.translation_table.resolve_term("expressed in")

try:
    gene_id = get_data(row, "geneId")
    # Not sure if Alliance will stick with this prefix for Xenbase, but for now...
    gene_id = gene_id.replace("DRSC:XB:", "Xenbase:")

    # TODO: Biolink Model provenance likely needs to be changed
    #       soon to something like "aggregating_knowledge_source"
    db = gene_id.split(":")[0]
    source = source_map[db]

    cellular_component_id = get_data(row, "whereExpressed.cellularComponentTermId")
    anatomical_entity_id = get_data(row, "whereExpressed.anatomicalStructureTermId")

    stage_term_id = get_data(row, "whenExpressed.stageTermId")
    # if not stage_term_id:
    # TODO: some databases (e.g. MGI) do not stageTermId's
    #       but may have an UBERON term that we can use
    # stage_term_id = get_data(row, "whenExpressed.stageUberonSlimTerm.uberonTerm")

    evidence = list()
    assay = get_data(row, "assay")  # e.g. "MMO:0000658"
    if assay:
        evidence.append(assay)

    xref = get_data(row, "crossReference.id")
    if xref:
        evidence.append(xref)

    publication_ids = get_data(row, "evidence.publicationId")

    # Our current ingest policy is to first use a reported Anatomical structure term...
    if anatomical_entity_id:
        koza_app.write(
            GeneToExpressionSiteAssociation(
                id="uuid:" + str(uuid.uuid1()),
                subject=gene_id,
                predicate='biolink:expressed_in',
                object=anatomical_entity_id,
                stage_qualifier=stage_term_id,
                has_evidence=evidence,
                publications=[publication_ids],
                aggregating_knowledge_source=["infores:monarchinitiative", "infores:alliancegenome"],
                primary_knowledge_source=source
            )
        )

    elif cellular_component_id:
        # ... and failing that, fall back to using a subcellular component
        # (but ignore otherwise ignore it, if reported alongside in the record)
        koza_app.write(
            GeneToExpressionSiteAssociation(
                id="uuid:" + str(uuid.uuid1()),
                subject=gene_id,
                predicate='biolink:expressed_in',
                object=cellular_component_id,
                stage_qualifier=stage_term_id,
                has_evidence=evidence,
                publications=[publication_ids],
                aggregating_knowledge_source=["infores:monarchinitiative", "infores:alliancegenome"],
                primary_knowledge_source=source
            )
        )
    else:
        # Print a log error and skip the S-P-O ingest
        logger.error(
            f"Gene expression record: \n\t'{str(row)}'\n has no ontology terms specified for expression site?"
        )

except Exception as exc:
    logger.error(
        f"Alliance gene expression ingest parsing exception for data row:\n\t'{str(row)}'\n{str(exc)}"
    )
