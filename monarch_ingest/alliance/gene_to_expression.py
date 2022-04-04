import logging
import uuid

from biolink_model_pydantic.model import (
    Gene,
    GeneToExpressionSiteAssociation,
    CellularComponent,
    AnatomicalEntity,
    Predicate
)
from koza.cli_runner import koza_app
from source_translation import source_map

from monarch_ingest.alliance.utils import get_taxon, get_data

logger = logging.getLogger(__name__)

source_name = "alliance_gene_to_expression"

row = koza_app.get_row(source_name)

EXPRESSED_IN_RELATION = koza_app.translation_table.resolve_term("expressed in")

try:
    gene_id = get_data(row, "geneId")

    db = gene_id.split(":")[0]
    source = source_map[db]

    ncbi_taxon_id = get_taxon(db)

    cellular_component_id = get_data(row, "whereExpressed.cellularComponentTermId")
    anatomical_entity_id = get_data(row, "whereExpressed.anatomicalStructureTermId")
    stage_term_id = get_data(row, "whenExpressed.stageTermId")

    evidence = list()
    assay = get_data(row, "assay")  # e.g. "MMO:0000658"
    if assay:
        evidence.append(assay)

    xref = get_data(row, "crossReference.id")
    if xref:
        evidence.extend(xref)

    publication_ids = get_data(row, "evidence.publicationId")

    if not (cellular_component_id or anatomical_entity_id):
        raise RuntimeError("Gene expression record has no anatomical entity expression site terms: " + str(row))
    #
    # TODO: having both component and anatomy id values is probably not a problem,
    #       but we'll have to handle this concurrency of location sensibly down below?
    #
    # elif row["CellularComponentID"] and row["AnatomyTermID"]:
    #     raise RuntimeError("Gene expression record has >1 anatomical entity expression site terms: " + str(row))
    else:
        gene = Gene(id=gene_id, in_taxon=ncbi_taxon_id, source=source)

        # TODO: For now, we write out separate gene expression site associations for each
        #       kind of expression localization, in case a single ingest record records both?
        cellular_component = anatomical_entity = None
        if cellular_component_id:
            cellular_component = \
                CellularComponent(
                    id=cellular_component_id,
                    in_taxon=ncbi_taxon_id,
                    source=source
                )
            association = GeneToExpressionSiteAssociation(
                id="uuid:" + str(uuid.uuid1()),
                subject=gene.id,
                predicate=Predicate.expressed_in,
                relation=EXPRESSED_IN_RELATION,
                object=cellular_component.id,
                stage_qualifier=stage_term_id,
                has_evidence=evidence,
                publications=publication_ids,
                source=source
            )

            koza_app.write(gene, cellular_component, association)

        if anatomical_entity_id:
            anatomical_entity = \
                AnatomicalEntity(
                    id=anatomical_entity_id,
                    in_taxon=ncbi_taxon_id,
                    source=source
                )
            association = GeneToExpressionSiteAssociation(
                id="uuid:" + str(uuid.uuid1()),
                subject=gene.id,
                predicate=Predicate.expressed_in,
                relation=EXPRESSED_IN_RELATION,
                object=anatomical_entity.id,
                stage_qualifier=stage_term_id,
                has_evidence=evidence,
                publications=publication_ids,
                source=source
            )

            koza_app.write(gene, anatomical_entity, association)

except Exception as exc:
    logger.error(f"Invalid Alliance gene expression record: {str(exc)}")
