"""
Gene Ontology Annotations Ingest module.

Gene to GO term Associations
(to MolecularActivity, BiologicalProcess and CellularComponent)
"""
import re
import uuid
import logging

from biolink_model_pydantic.model import (
    Gene,
    Predicate,
    MacromolecularMachineToMolecularActivityAssociation,
    MacromolecularMachineToBiologicalProcessAssociation,
    MacromolecularMachineToCellularComponentAssociation
)

from koza.cli_runner import koza_app

from monarch_ingest.goa.goa_utils import (
    molecular_function,
    biological_process,
    cellular_component,
    lookup_predicate,
    DEFAULT_RELATIONSHIP,
    infer_cellular_component_predicate
)

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

row = koza_app.get_row()

db = row['DB']
db_object_id = row['DB_Object_ID']
db_id = f"{db}:{db_object_id}"

# TODO: need to remap this DB id onto a proper gene id (db_id is probably probably a uniprot id?)
gene_id = db_id

ncbitaxon = row['Taxon']
if ncbitaxon:
    ncbitaxon = re.sub(r"^taxon", "NCBITaxon", ncbitaxon, flags=re.IGNORECASE)

# TODO: wrong.. gene_id is likely a protein identifier right now... not yet translated to an Entrez ID?
gene = Gene(id=gene_id, in_taxon=ncbitaxon, source="infores:entrez")

association = None  # in case of a go_id which doesn't hit anything?

# The Association Predicate and Relation are
# inferred from the GAF 'Qualifier' used.
# Note that this qualifier may be negated (i.e. "NOT|<qualifier>").
predicate, relation = DEFAULT_RELATIONSHIP
negated = False
qualifier = row['Qualifier']
if qualifier:
    # check for piped negation prefix (hopefully, well behaved!)
    qualifier_parts = qualifier.split("|")
    if qualifier_parts[0] == "NOT":
        predicate, relation = lookup_predicate(qualifier_parts[1])
        negated = True
    else:
        predicate, relation = lookup_predicate(qualifier_parts[0])

# The GO Evidence Code is useful ...
evidence_code = row['Evidence_Code']

# TODO: could any of the GAF rows have multiple GO_ID entries? check the spec...
go_id = row['GO_ID']

# TODO: need to figure out which GO identifier space this term belongs to:
#       molecular_function - child of GO:0003674,
#       biological_process - child of GO:0008150 OR
#       cellular_component - child of GO:0005575
#       Note that since GO is a DAG, these terms can have multiple parents...how do we handle this?
#
# TODO: For root node annotations that use the ND evidence code, the following relations should be used:
#       biological_process (GO:0008150) involved_in (RO:0002331)
#       molecular_function (GO:0003674) enables (RO:0002327)
#       cellular_component (GO:0005575) is_active_in (RO:0002432)

# First naive iteration... probably wrong!
go_term = molecular_function(go_id)
if go_term:
    
    if not predicate:
        # use a reasonable predicate default, if necessary
        predicate = Predicate.enables
    
    association = MacromolecularMachineToMolecularActivityAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene.id,
        object=go_term.id,
        predicate=predicate,
        relation=relation,
        has_evidence=evidence_code,
        source="infores:goa",
    )
else:
    go_term = biological_process(go_id)
    if go_term:
    
        if not predicate:
            # use a reasonable predicate default, if necessary
            predicate = Predicate.acts_upstream_of_or_within
    
        association = MacromolecularMachineToBiologicalProcessAssociation(
            id="uuid:" + str(uuid.uuid1()),
            subject=gene.id,
            object=go_term.id,
            predicate=predicate,
            relation=relation,
            has_evidence=evidence_code,
            source="infores:goa",
        )
    else:
        go_term = cellular_component(go_id)
        if go_term:
    
            if not predicate:
                predicate = infer_cellular_component_predicate(go_term)
    
            association = MacromolecularMachineToCellularComponentAssociation(
                id="uuid:" + str(uuid.uuid1()),
                subject=gene.id,
                object=go_term.id,
                predicate=predicate,
                relation=relation,
                has_evidence=evidence_code,
                source="infores:goa",
            )
        else:
            logger.warning(f"go_annotation(): Unresolved go_term: {str(go_id)}? Ignored...")

if association:
    koza_app.write(gene_id, go_id, association)
