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

gene_ids = koza_app.get_map("alliance-gene")

source_name = "alliance_gene_to_expression"

row = koza_app.get_row(source_name)

source = None

try:
    gene_id = row["GeneID"]
    ncbitaxon_id = row["SpeciesID"]
    stage_term = row["StageTerm"]
    assay_id = row["AssayID"]  # e.g. "MMO:0000658",
    # assay_term_name = row["AssayTermName"]  # e.g. "ribonucleic acid in situ hybridization assay"
    cellular_component_id = row["CellularComponentID"]  # Probably a GO term; None otherwise
    anatomical_entity_id = row["AnatomyTermID"]  # Likely a ZFIN anatomical term id or equivalent in other species

    # Identify the source
    source = source_map[gene_id.split(':')[0]]

    publication_ids = row["Reference"]  # should be a List of Pubmed identifiers

    if not (cellular_component_id or anatomical_entity_id):
        raise RuntimeError("Gene expression record has no anatomical entity expression site terms: " + str(row))
        #
        # Maybe not a problem, but perhaps we'll have to handle this sensibly down below?
        #
        # elif row["CellularComponentID"] and row["AnatomyTermID"]:
        #     raise RuntimeError("Gene expression record has >1 anatomical entity expression site terms: " + str(row))

    # Limit to mappable gene id's?
    elif gene_id not in gene_ids.keys():
        raise RuntimeError(f"Gene {gene_id} in the gene expression record not in gene map")
    else:

        gene = Gene(id=gene_id, in_taxon=ncbitaxon_id, source=source)

        life_stage: Optional[LifeStage] = None
        if stage_term:
            life_stage = get_life_stage(species=ncbitaxon_id, stage_term=stage_term)

        # TODO: For now, we write out separate gene expression site associations
        #       for each kind of localization, in case a single record records both?
        cellular_component = anatomical_entity = None
        if cellular_component_id:
            cellular_component = CellularComponent(id=cellular_component_id, source=source)
            association = GeneToExpressionSiteAssociation(
                id="uuid:" + str(uuid.uuid1()),
                subject=gene.id,
                predicate=Predicate.expressed_in,
                object=cellular_component.id,
                stage_qualifier=life_stage,
                has_evidence=[assay_id],
                publications=publication_ids,
                source=source
            )

            koza_app.write(gene, cellular_component, association)

        if anatomical_entity_id:
            anatomical_entity = AnatomicalEntity(id=anatomical_entity_id, source=source)
            association = GeneToExpressionSiteAssociation(
                id="uuid:" + str(uuid.uuid1()),
                subject=gene.id,
                predicate=Predicate.expressed_in,
                object=anatomical_entity.id,
                stage_qualifier=life_stage,
                has_evidence=[assay_id],
                publications=publication_ids,
                source=source
            )

            koza_app.write(gene, anatomical_entity, association)

except Exception as exc:
    logger.error(f"Invalid Alliance gene expression record: {str(exc)}")
