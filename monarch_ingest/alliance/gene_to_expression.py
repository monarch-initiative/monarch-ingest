from typing import Optional

import logging
import uuid

from biolink_model_pydantic.model import (
    Gene,
    GeneToExpressionSiteAssociation,
    CellularComponent,
    AnatomicalEntity,
    Predicate, LifeStage
)
from koza.cli_runner import koza_app
from source_translation import source_map

from monarch_ingest.alliance.utils import get_life_stage

logger = logging.getLogger(__name__)

source_name = "alliance_gene_to_expression"

row = koza_app.get_row(source_name)

EXPRESSED_IN_RELATION = koza_app.translation_table.resolve_term("expressed in")

try:
    gene_id = row["GeneID"]
    gene_symbol = row["GeneSymbol"]
    ncbi_taxon_id = row["SpeciesID"]

    cellular_component_id = row["CellularComponentID"]
    cellular_component_name = row["CellularComponentTerm"]

    anatomical_entity_id = row["AnatomyTermID"]
    anatomical_entity_name = row["AnatomyTermName"]

    stage_term = row["StageTerm"]

    evidence = list()
    assay_id = row["AssayID"]  # e.g. "MMO:0000658"
    # assay_term_name = row["AssayTermName"]  # e.g. "ribonucleic acid in situ hybridization assay"
    if assay_id:
        evidence.append(assay_id)

    source_url = row["SourceURL"]
    if source_url:
        evidence.append(source_url)

    db = row['Source']
    source = source_map[db]

    publication_ids = row["Reference"]  # should be a List of Pubmed CURIEs or equivalent (e.g. Flybase citation)

    if not (cellular_component_id or anatomical_entity_id):
        raise RuntimeError("Gene expression record has no anatomical entity expression site terms: " + str(row))

    #
    # TODO: having both component and anatomy id values may not be a problem,
    #       but perhaps we'll have to handle this sensibly down below?
    #
    # elif row["CellularComponentID"] and row["AnatomyTermID"]:
    #     raise RuntimeError("Gene expression record has >1 anatomical entity expression site terms: " + str(row))
    else:

        gene = Gene(id=gene_id, name=gene_symbol, in_taxon=ncbi_taxon_id, source=source)

        life_stage: Optional[LifeStage] = None
        if stage_term:
            life_stage = get_life_stage(db=db, ncbi_taxon_id=ncbi_taxon_id, stage_term=stage_term)

        # TODO: For now, we write out separate gene expression site associations for each
        #       kind of expression localization, in case a single ingest record records both?
        cellular_component = anatomical_entity = None
        if cellular_component_id:
            cellular_component = \
                CellularComponent(
                    id=cellular_component_id,
                    name=cellular_component_name,
                    source=source
                )
            association = GeneToExpressionSiteAssociation(
                id="uuid:" + str(uuid.uuid1()),
                subject=gene.id,
                predicate=Predicate.expressed_in,
                relation=EXPRESSED_IN_RELATION,
                object=cellular_component.id,
                stage_qualifier=life_stage,
                has_evidence=evidence,
                publications=publication_ids,
                source=source
            )

            koza_app.write(gene, cellular_component, association)

        if anatomical_entity_id:
            anatomical_entity = \
                AnatomicalEntity(
                    id=anatomical_entity_id,
                    name=anatomical_entity_name,
                    source=source
                )
            association = GeneToExpressionSiteAssociation(
                id="uuid:" + str(uuid.uuid1()),
                subject=gene.id,
                predicate=Predicate.expressed_in,
                relation=EXPRESSED_IN_RELATION,
                object=anatomical_entity.id,
                stage_qualifier=life_stage,
                has_evidence=evidence,
                publications=publication_ids,
                source=source
            )

            koza_app.write(gene, anatomical_entity, association)

except Exception as exc:
    logger.error(f"Invalid Alliance gene expression record: {str(exc)}")
