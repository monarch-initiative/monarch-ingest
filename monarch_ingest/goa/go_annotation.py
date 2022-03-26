"""
Gene Ontology Annotations Ingest module.

Gene to GO term Associations
(to MolecularActivity, BiologicalProcess and CellularComponent)
"""
import logging
import re
import uuid
from typing import List

from biolink_model_pydantic.model import Gene
from koza.cli_runner import koza_app

from monarch_ingest.goa.goa_utils import get_biolink_classes, lookup_predicate

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

row = koza_app.get_row()

db = row['DB']
db_object_id = row['DB_Object_ID']

# This check is to avoid MGI:MGI:123
if ":" in db_object_id:
    object_id = db_object_id
else:
    object_id = f"{db}:{db_object_id}"

# The biolink model might be wrong here about all caps, but matching it for now
gene_id = object_id.replace('PomBase', 'POMBASE')

ncbitaxon = row['Taxon']
if ncbitaxon:
    # in rare circumstances, multiple taxa may be given as a piped list...
    taxa = ncbitaxon.split("|")
    ncbitaxon: List[str] = list()
    for taxon in taxa:
        ncbitaxon.append(re.sub(r"^taxon", "NCBITaxon", taxon, flags=re.IGNORECASE))
else:
    # Unlikely to happen, but...
    logger.warning(f"Missing taxon for '{object_id}'?")


# Grab the Gene Ontology ID
go_id = row['GO_ID']

# Discern GO identifier 'aspect'' this term belongs to:
#      'F' == molecular_function - child of GO:0003674
#      'P' == biological_process - child of GO:0008150
#      'C' == cellular_component - child of GO:0005575
go_aspect: str = row['Aspect']
if not (go_aspect and go_aspect.upper() in ["F", "P", "C"]):
    logger.warning(
        f"GAF Aspect '{str(go_aspect)}' is empty or unrecognized? Skipping record"
    )

else:
    # Decipher the GO Evidence Code
    evidence_code = row['Evidence_Code']
    eco_term = None

    if evidence_code and evidence_code in koza_app.translation_table.local_table:
        eco_term = koza_app.translation_table.local_table[evidence_code]

    if not eco_term:
        logger.warning(
            f"GAF Evidence Code '{str(evidence_code)}' is empty or unrecognized? Tagging as 'ND'"
        )
        eco_term = "ECO:0000307"

    # Association predicate is normally NOT negated
    # except as noted below in the GAF qualifier field
    negated = False

    # For root node annotations that use the ND evidence code,
    # the following relations should be used:
    #
    #     molecular_function (GO:0003674) enables (RO:0002327)
    #     biological_process (GO:0008150) involved_in (RO:0002331)
    #     cellular_component (GO:0005575) is_active_in (RO:0002432)
    #
    relation = predicate = predicate_mapping = qualifier = None
    if go_id == "GO:0003674" and eco_term == "ECO:0000307":
        qualifier = "enables"
    elif go_id == "GO:0008150" and eco_term == "ECO:0000307":
        qualifier = "involved_in"
    elif go_id == "GO:0005575" and eco_term == "ECO:0000307":
        qualifier = "is_active_in"
    else:
        # The Association Predicate and Relation are otherwise inferred from the GAF 'Qualifier' used.
        # Note that this qualifier may be negated (i.e. "NOT|<qualifier>").
        qualifier = row['Qualifier']

    if not qualifier:
        # If missing, assign a default qualifier a.k.a. predicate based on specified GO Aspect type
        logger.error(
            "GAF record is missing its qualifier...assigning default qualifier as per GO term Aspect"
        )
        if go_aspect == "F":
            qualifier = "enables"
        elif go_aspect == "P":
            qualifier = "involved_in"
        elif go_aspect == "C":
            qualifier = "located_in"

    else:
        # check for piped negation prefix (hopefully, well behaved!)
        qualifier_parts = qualifier.split("|")
        if qualifier_parts[0] == "NOT":
            predicate_mapping = lookup_predicate(qualifier_parts[1])
            negated = True
        else:
            predicate_mapping = lookup_predicate(qualifier_parts[0])

        if not predicate_mapping:
            logger.error(
                f"GAF Qualifier '{qualifier}' is unrecognized? Skipping the record..."
            )

        else:
            # extract the predicate Pydantic class and RO'relation' mapping
            # TODO: the Biolink Model may soon deprecate the 'relation' field?
            predicate, relation = predicate_mapping

            # Retrieve the GO aspect related NamedThing category-associated 'node' and Association 'edge' classes
            go_concept_node_class, gene_go_term_association_class = get_biolink_classes(
                go_aspect
            )

            # Instantiate the GO term instance
            go_term = go_concept_node_class(id=go_id, source="infores:go")

            # Instantiate the appropriate Gene-to-GO Term instance
            association = gene_go_term_association_class(
                id="uuid:" + str(uuid.uuid1()),
                subject=object_id,
                object=go_id,
                predicate=predicate,
                negated=negated,
                relation=relation,
                has_evidence=eco_term,
                source="infores:goa",
            )

            # Write the captured Association out
            koza_app.write(association)
