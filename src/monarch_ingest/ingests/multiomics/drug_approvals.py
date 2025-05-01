import uuid
from typing import Dict, Any

from koza.cli_utils import get_koza_app

from biolink_model.datamodel.pydanticmodel_v2 import (
    ChemicalToDiseaseOrPhenotypicFeatureAssociation,
    KnowledgeLevelEnum,
    AgentTypeEnum, NamedThing,
)
from monarch_ingest.constants import BIOLINK_TREATS, BIOLINK_APPROVED_FOR_TREATMENT
from monarch_ingest.ingests.multiomics.clinical_trials import CATEGORY_CLASS_MAP

"""
Transforms drug approvals data from multiomics KP into Biolink model compliant nodes and edges.
"""

ALLOWED_CHEMICAL_CATEGORIES = [
    "biolink:ChemicalEntity",
    "biolink:SmallMolecule",
    "biolink:MolecularMixture"
]

def is_valid_chemical_entity(row: Dict[str, Any]) -> bool:
    """
    Checks if a node is a valid chemical entity based on its category.
    
    Args:
        row: A dictionary representing a row from the input file
        
    Returns:
        bool: True if the node is a valid chemical entity, False otherwise
    """
    return row.get('category') in ALLOWED_CHEMICAL_CATEGORIES

def transform_node(row: Dict[str, Any]) -> NamedThing:
    """
    Transforms a node row into a standardized format.
    
    Args:
        row: A dictionary representing a row from the input file
        
    Returns:
        Dict: A transformed node record
    """
    category = row.get("category")
    cls = CATEGORY_CLASS_MAP.get(category, NamedThing)
    node = cls(
        id=row["id"],
        name=row.get("name"),
        category=[row["category"]]
    )
    return node

def transform_edge(row: Dict[str, Any]) -> ChemicalToDiseaseOrPhenotypicFeatureAssociation:
    """
    Transforms an edge row into a Chemical to Disease association.
    
    Args:
        row: A dictionary representing a row from the input file
        
    Returns:
        ChemicalToDiseaseOrPhenotypicFeatureAssociation: A biolink model association
    """
    subject_id = row.get('subject')
    object_id = row.get('object')
    
    predicate = (
        BIOLINK_APPROVED_FOR_TREATMENT 
        if row.get('predicate') == 'biolink:approved_for_treatment' 
        else BIOLINK_TREATS
    )
    
    association = ChemicalToDiseaseOrPhenotypicFeatureAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=subject_id,
        predicate=predicate,
        object=object_id,
        publications=row.get('publications', []),  # List of PMIDs if available
        aggregator_knowledge_source=["infores:monarchinitiative"],
        primary_knowledge_source="infores:multiomics-kp",
        knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
        agent_type=AgentTypeEnum.automated_agent,
    )
    
    return association

def process_nodes(koza_app=None):
    """Process drug approvals nodes file to extract chemical entities."""
    if koza_app is None:
        koza_app = get_koza_app("multiomics_drug_approvals")
    
    while (row := koza_app.get_row()) is not None:
        if is_valid_chemical_entity(row):
            node = transform_node(row)
            koza_app.write(node)

def process_edges(koza_app=None):
    """Process drug approvals edges file to extract chemical-disease associations."""
    if koza_app is None:
        koza_app = get_koza_app("multiomics_drug_approvals")
    
    while (row := koza_app.get_row()) is not None:
        if row.get('predicate') in ['biolink:treats', 'biolink:approved_for_treatment']:
            association = transform_edge(row)
            koza_app.write(association)

