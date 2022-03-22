import logging
import uuid

from biolink_model_pydantic.model import (
    Gene,
    GeneToExpressionSiteAssociation,
    GeneExpressionMixin,
    Predicate,
)
from koza.cli_runner import koza_app
from source_translation import source_map

LOG = logging.getLogger(__name__)

source_name = "alliance_gene_to_expression"

row = koza_app.get_row(source_name)
gene_ids = koza_app.get_map("alliance-gene")

if len(row["expressionTermIdentifiers"]) == 0:
    LOG.warning("expression ingest record has 0 expression terms: " + str(row))

if len(row["expressionTermIdentifiers"]) > 1:
    LOG.warning("expression ingest record has >1 expression terms: " + str(row))

# limit to only genes
if row["objectId"] in gene_ids.keys() and len(row["expressionTermIdentifiers"]) == 1:

    source = source_map[row["objectId"].split(':')[0]]

    pheno_id = row["expressionTermIdentifiers"][0]["termId"]
    # Remove the extra WB: prefix if necessary
    pheno_id = pheno_id.replace("WB:WBexpression:", "WBexpression:")

    gene = Gene(id=row["objectId"], source=source)
    expressionFeature = GeneExpressionMixin(id=pheno_id, source=source)
    association = GeneToExpressionSiteAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene.id,
        predicate=Predicate.has_expression,
        object=expressionFeature.id,
        relation=koza_app.translation_table.resolve_term("has expression"),
        publications=[row["evidence"]["publicationId"]],
        source=source,
    )

    if "expressionRelations" in row.keys() and row["expressionRelations"] is not None:
        qualifiers = []
        for expressionRelation in row["expressionRelations"]:
            for expression in expressionRelation["expressions"]:
                if expression["expressionClassId"]:
                    qualifiers.append(expression["expressionClassId"])
        association.qualifiers = qualifiers

    koza_app.write(gene, expressionFeature, association)
