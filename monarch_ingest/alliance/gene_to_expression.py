import logging
import uuid

from biolink_model_pydantic.model import (GeneToExpressionSiteAssociation, Predicate)
from koza.cli_runner import koza_app
from source_translation import source_map

from monarch_ingest.alliance.utils import get_data

logger = logging.getLogger(__name__)

source_name = "alliance_gene_to_expression"

row = koza_app.get_row(source_name)

EXPRESSED_IN_RELATION = koza_app.translation_table.resolve_term("expressed in")

try:
    gene_id = get_data(row, "geneId")

    # TODO: Biolink Model provenance likely needs to be changed
    #       soon to something like "aggregating_knowledge_source"
    db = gene_id.split(":")[0]
    source = source_map[db]
    provided_by = source

    cellular_component_id = get_data(row, "whereExpressed.cellularComponentTermId")
    anatomical_entity_id = get_data(row, "whereExpressed.anatomicalStructureTermId")
    stage_term_id = get_data(row, "whenExpressed.stageTermId")

    evidence = list()
    assay = get_data(row, "assay")  # e.g. "MMO:0000658"
    if assay:
        evidence.append(assay)

    xref = get_data(row, "crossReference.id")
    if xref:
        evidence.append(xref)

    publication_ids = get_data(row, "evidence.publicationId")

    if not (anatomical_entity_id or cellular_component_id):
        # Print a log error and skip the S-P-O ingest
        logger.error(f"Gene expression record: \n\t'{str(row)}'\n has no ontology terms specified for expression site?")
    else:
        #
        # TODO: having both component and anatomy id values is probably not a problem, but we'll
        #       have to deal with this concurrency of location information sensibly down below?
        #
        if anatomical_entity_id and cellular_component_id:
            logger.warning(
                "Gene expression record has both " +
                f"a Cellular Component term '{cellular_component_id}' " +
                f"and an Anatomy Term '{anatomical_entity_id}'? I will try to capture both..."
            )

        # TODO: For now, we write out separate gene expression site associations for each
        #       type of gene expression localization, in case a single ingest row records both?
        if cellular_component_id:
            koza_app.write(
                GeneToExpressionSiteAssociation(
                    id="uuid:" + str(uuid.uuid1()),
                    subject=gene_id,
                    predicate=Predicate.expressed_in,
                    relation=EXPRESSED_IN_RELATION,
                    object=cellular_component_id,
                    stage_qualifier=stage_term_id,
                    has_evidence=evidence,
                    publications=publication_ids,
                    provided_by=provided_by,
                    source=source
                )
            )

        if anatomical_entity_id:
            koza_app.write(
                GeneToExpressionSiteAssociation(
                    id="uuid:" + str(uuid.uuid1()),
                    subject=gene_id,
                    predicate=Predicate.expressed_in,
                    relation=EXPRESSED_IN_RELATION,
                    object=anatomical_entity_id,
                    stage_qualifier=stage_term_id,
                    has_evidence=evidence,
                    publications=publication_ids,
                    provided_by=provided_by,
                    source=source
                )
            )

except Exception as exc:
    logger.error(f"Alliance gene expression ingest parsing exception for data row:\n\t'{str(row)}'\n{str(exc)}")
