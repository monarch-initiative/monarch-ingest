import koza
import uuid
import pandas as pd
from biolink_model.datamodel.pydanticmodel_v2 import GeneToExpressionSiteAssociation, KnowledgeLevelEnum, AgentTypeEnum


@koza.transform()
def transform_bgee_data(koza_transform, data):
    """
    Transform bgee data with complex group ranking logic preserved.
    This processes all data at once to enable grouping and ranking.
    """
    # Convert to pandas for efficient group processing
    df = pd.DataFrame(data)

    # Group by Gene ID and apply ranking logic
    for gene_id, group in df.groupby('Gene ID'):
        # Get top 10 rows with smallest Expression rank for this gene
        # Sort by Expression rank and take first 10 (smallest ranks)
        top_rows = group.nsmallest(10, 'Expression rank', keep='first')

        # Process each row in the top-ranked group
        for _, row in top_rows.iterrows():
            obj = row['Anatomical entity ID']
            anatomical_entities = row['Anatomical entity ID'].split(' ∩ ')
            object_specialization_qualifier = None

            if len(anatomical_entities) == 2:
                if ':' not in anatomical_entities[0] or ':' not in anatomical_entities[1]:
                    # Skip invalid CURIE formats
                    continue
                obj = anatomical_entities[0]
                object_specialization_qualifier = anatomical_entities[1]

            association = GeneToExpressionSiteAssociation(
                id="uuid:" + str(uuid.uuid1()),
                subject="ENSEMBL:" + row['Gene ID'],
                predicate='biolink:expressed_in',
                object=obj,
                primary_knowledge_source="infores:bgee",
                aggregator_knowledge_source=["infores:monarchinitiative"],
                knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
                agent_type=AgentTypeEnum.not_provided,
                object_specialization_qualifier=object_specialization_qualifier,
            )

            koza_transform.write(association)
