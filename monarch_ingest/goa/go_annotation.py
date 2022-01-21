"""
Gene Ontology Annotations Ingest module.

Gene to GO term Associations
(to MolecularActivity, BiologicalProcess and CellularComponent)
"""
import re
import uuid
import logging

from koza.cli_runner import koza_app
from biolink_model_pydantic.model import Gene
from monarch_ingest.goa.goa_utils import lookup_predicate, get_biolink_classes

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

row = koza_app.get_row()

gec_2_et = koza_app.get_map('gaf_evidence_code_2_eco_term')

db = row['DB']
db_object_id = row['DB_Object_ID']
db_id = f"{db}:{db_object_id}"

# TODO: need to remap this DB id onto a proper gene id (db_id is probably probably a uniprot id?)
gene_id = db_id

ncbitaxon = row['Taxon']
if ncbitaxon:
    ncbitaxon = re.sub(r"^taxon", "NCBITaxon", ncbitaxon, flags=re.IGNORECASE)

# TODO: wrong.. gene_id is likely a protein identifier right now... not yet translated to an Entrez ID?
gene = Gene(id=gene_id, in_taxon=ncbitaxon, source="infores:uniprot")

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
    if evidence_code and evidence_code in gec_2_et:
        eco_term = gec_2_et[evidence_code]
    else:
        logger.warning(f"GAF Evidence Code '{str(evidence_code)}' is empty or unrecognized? Tagging as 'ND'")
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
        # Can't process this record without a GAF qualifier? Shouldn't usually happen...
        logger.error("GAF record is missing its qualifier...skipping")
    else:
        # check for piped negation prefix (hopefully, well behaved!)
        qualifier_parts = qualifier.split("|")
        if qualifier_parts[0] == "NOT":
            predicate_mapping = lookup_predicate(qualifier_parts[1])
            negated = True
        else:
            predicate_mapping = lookup_predicate(qualifier_parts[0])
        
        if not predicate_mapping:
            logger.error(f"GAF Qualifier '{qualifier}' is unrecognized? Skipping the record...")
    
        else:
            # extract the predicate Pydantic class and RO'relation' mapping
            # TODO: the Biolink Model may soon deprecate the 'relation' field?
            predicate, relation = predicate_mapping
    
            # Retrieve the GO aspect related NamedThing category-associated 'node' and Association 'edge' classes
            go_concept_node_class, gene_go_term_association_class = get_biolink_classes(go_aspect)
    
            # Instantiate the GO term instance
            go_term = go_concept_node_class(id=go_id)
    
            # Instantiate the appropriate Gene-to-GO Term instance
            association = gene_go_term_association_class(
                id="uuid:" + str(uuid.uuid1()),
                subject=gene.id,
                object=go_term.id,
                predicate=predicate,
                relation=relation,
                has_evidence=eco_term,
                source="infores:goa"
            )
            
            # Write the captured Association out
            koza_app.write(gene, go_term, association)
