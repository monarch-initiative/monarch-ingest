import uuid
from typing import Dict, Any

from koza.cli_utils import get_koza_app

from biolink_model.datamodel.pydanticmodel_v2 import (
    ChemicalToDiseaseOrPhenotypicFeatureAssociation,
    KnowledgeLevelEnum,
    AgentTypeEnum, NamedThing, ChemicalEntity, SmallMolecule, MolecularMixture,
)

from monarch_ingest.constants import BIOLINK_IN_CLINICAL_TRIAL_FOR

BIOLINK_IN_CLINICAL_TRIALS_FOR = 'biolink:in_clinical_trials_for'

"""
Transforms clinical trials data from multiomics KP into Biolink model compliant nodes and edges.
"""

ALLOWED_CHEMICAL_CATEGORIES = [
    "biolink:ChemicalEntity",
    "biolink:SmallMolecule",
    "biolink:MolecularMixture"
]

CATEGORY_CLASS_MAP = {
    "biolink:ChemicalEntity": ChemicalEntity,
    "biolink:SmallMolecule": SmallMolecule,
    "biolink:MolecularMixture": MolecularMixture,
}

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
    Transforms a node row into a Biolink-Model Pydantic object.
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
    
    association = ChemicalToDiseaseOrPhenotypicFeatureAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=subject_id,
        predicate=BIOLINK_IN_CLINICAL_TRIAL_FOR,
        object=object_id,
        publications=row.get('publications', []),
        aggregator_knowledge_source=["infores:monarchinitiative"],
        primary_knowledge_source="infores:multiomics-kp",
        knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
        agent_type=AgentTypeEnum.automated_agent,
    )
    
    return association

def process_nodes(koza_app=None):
    """Process clinical trials nodes file to extract chemical entities."""
    if koza_app is None:
        koza_app = get_koza_app("multiomics_clinical_trials")
    
    while (row := koza_app.get_row()) is not None:
        if is_valid_chemical_entity(row):
            node = transform_node(row)
            koza_app.write(node)

def process_edges(koza_app=None):
    """Process clinical trials edges file to extract chemical-disease associations."""
    if koza_app is None:
        koza_app = get_koza_app("multiomics_clinical_trials")
    
    while (row := koza_app.get_row()) is not None:
        if row.get('predicate') == BIOLINK_IN_CLINICAL_TRIALS_FOR:
            association = transform_edge(row)
            koza_app.write(association)

