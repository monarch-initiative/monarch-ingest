"""
Gene Ontology Annotations Ingest module.

Gene to GO term Associations
(to MolecularActivity, BiologicalProcess and CellularComponent)
"""

import uuid

from biolink_model.datamodel.pydanticmodel_v2 import KnowledgeLevelEnum, AgentTypeEnum
from koza.cli_utils import get_koza_app

from monarch_ingest.ingests.go.annotation_utils import (
    parse_identifiers,
    get_biolink_classes,
    lookup_predicate,
    get_infores,
)
from loguru import logger


koza_app = get_koza_app("go_annotation")

# for row in koza_app.source: # doesn't play nice with tests
while (row := koza_app.get_row()) is not None:

    gene_id, ncbitaxa = parse_identifiers(row)

    # Grab the Gene Ontology ID
    go_id = row['GO_ID']

    # Discern GO identifier 'aspect'' this term belongs to:
    #      'F' == molecular_function - child of GO:0003674
    #      'P' == biological_process - child of GO:0008150
    #      'C' == cellular_component - child of GO:0005575
    go_aspect: str = row['Aspect']
    if not (go_aspect and go_aspect.upper() in ["F", "P", "C"]):
        logger.warning(f"GAF Aspect '{str(go_aspect)}' is empty or unrecognized? Skipping record")

    else:
        # Decipher the GO Evidence Code
        evidence_code = row['Evidence_Code']
        eco_term = None

        if evidence_code and evidence_code in koza_app.translation_table.local_table:
            eco_term = koza_app.translation_table.local_table[evidence_code]

        if not eco_term:
            logger.warning(f"GAF Evidence Code '{str(evidence_code)}' is empty or unrecognized? Tagging as 'ND'")
            eco_term = "ECO:0000307"

        # Association predicate is normally NOT negated
        # except as noted below in the GAF qualifier field
        negated = False

        # For root node annotations that use the ND evidence code should be used:
        #
        #     molecular_function (GO:0003674) enables (RO:0002327)
        #     biological_process (GO:0008150) involved_in (RO:0002331)
        #     cellular_component (GO:0005575) is_active_in (RO:0002432)
        #
        predicate = None
        if go_id == "GO:0003674" and eco_term == "ECO:0000307":
            qualifier = "enables"
        elif go_id == "GO:0008150" and eco_term == "ECO:0000307":
            qualifier = "involved_in"
        elif go_id == "GO:0005575" and eco_term == "ECO:0000307":
            qualifier = "is_active_in"
        else:
            # The Association Predicate is otherwise inferred from the GAF 'Qualifier' used.
            # Note that this qualifier may be negated (i.e. "NOT|<qualifier>").
            qualifier = row['Qualifier']

        if qualifier:
            # check for piped negation prefix (hopefully, well behaved!)
            qualifier_parts = qualifier.split("|")
            if qualifier_parts[0] == "NOT":
                predicate = lookup_predicate(qualifier_parts[1])
                negated = True
            else:
                predicate = lookup_predicate(qualifier_parts[0])
        else:
            # If qualifier missing, assign a default predicate
            # a.k.a. predicate based on specified GO Aspect type
            logger.error("GAF record is missing its qualifier...assigning default qualifier as per GO term Aspect")
            if go_aspect == "F":
                predicate = "enables"
            elif go_aspect == "P":
                predicate = "involved_in"
            elif go_aspect == "C":
                predicate = "located_in"

        if not predicate:
            logger.error(f"GAF Qualifier '{str(qualifier)}' is unrecognized? Skipping the record...")

        else:

            # Retrieve the GO aspect related NamedThing category-associated 'node' and Association 'edge' classes
            go_concept_node_class, gene_go_term_association_class = get_biolink_classes(go_aspect)

            # actual primary knowledge source of the GOA knowledge statement
            assigned_by = get_infores(row['Assigned_By'])

            # Instantiate the appropriate Gene-to-GO Term instance
            association = gene_go_term_association_class(
                id="uuid:" + str(uuid.uuid1()),
                subject=gene_id,
                object=go_id,
                predicate=predicate,
                negated=negated,
                has_evidence=[eco_term],
                # subject_context_qualifier=ncbitaxa,  # Biolink Pydantic model support missing for this slot
                aggregator_knowledge_source=["infores:monarchinitiative"],
                primary_knowledge_source=assigned_by,
                knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
                agent_type=AgentTypeEnum.manual_agent,
            )

            # Write the captured Association out
            koza_app.write(association)
