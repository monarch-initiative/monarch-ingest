import logging
import uuid

from biolink_model_pydantic.model import (
    Gene,
    GeneToPhenotypicFeatureAssociation,
    PhenotypicFeature,
    Predicate,
)

from koza.cli_runner import koza_app

# TODO: Probably not fit-for-purpose... just an exemplar for the EBI ingest?
from monarch_ingest.alliance.source_translation import source_map

LOG = logging.getLogger(__name__)

# You've got 'NCBI_Gene:' and you want 'NCBIGene:'? clean it up.
curie_cleaner = koza_app.curie_cleaner

source_name = "ebi_gene_to_phenotype"

row = koza_app.get_row(source_name)

# TODO: another exemplar for EBI - needs fixing
gene_ids = koza_app.get_map("alliance-gene")

if len(row["phenotypeTermIdentifiers"]) == 0:
    LOG.warning("Phenotype ingest record has 0 phenotype terms: " + str(row))

if len(row["phenotypeTermIdentifiers"]) > 1:
    LOG.warning("Phenotype ingest record has >1 phenotype terms: " + str(row))

# limit to only genes
if row["objectId"] in gene_ids.keys() and len(row["phenotypeTermIdentifiers"]) == 1:

    source = source_map[row["objectId"].split(':')[0]]

    pheno_id = row["phenotypeTermIdentifiers"][0]["termId"]
    # Remove the extra WB: prefix if necessary
    pheno_id = pheno_id.replace("WB:WBPhenotype:", "WBPhenotype:")

    gene = Gene(id=row["objectId"], source=source)

    # populate any additional optional gene properties
    if row['xrefs']:
        gene.xrefs = [curie_cleaner.clean(xref) for xref in row['xrefs']]

    phenotypicFeature = PhenotypicFeature(id=pheno_id, source=source)
    association = GeneToPhenotypicFeatureAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene.id,
        predicate=Predicate.has_phenotype,
        object=phenotypicFeature.id,
        relation=koza_app.translation_table.resolve_term("has phenotype"),
        publications=[row["evidence"]["publicationId"]],
        source=source,
    )

    if "conditionRelations" in row.keys() and row["conditionRelations"] is not None:
        qualifiers = []
        for conditionRelation in row["conditionRelations"]:
            for condition in conditionRelation["conditions"]:
                if condition["conditionClassId"]:
                    qualifiers.append(condition["conditionClassId"])
        association.qualifiers = qualifiers

    koza_app.write(association)
