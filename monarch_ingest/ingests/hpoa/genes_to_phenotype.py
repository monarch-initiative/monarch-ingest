import uuid

from koza.cli_runner import koza_app

from monarch_ingest.model.biolink import GeneToPhenotypicFeatureAssociation

source_name = "hpoa_genes_to_phenotype"
row = koza_app.get_row(source_name)

gene_id = "NCBIGene:" + row["entrez-gene-id"]
phenotype_id = row["HPO-Term-ID"]
disease_id = row["disease-ID for link"]
frequency_hpo = row["Frequency-HPO"]
qualifiers = [disease_id]
if frequency_hpo:
    # Not all entries have HPO frequency info
    qualifiers.append(frequency_hpo)
evidence = [row["G-D source"]]

association = GeneToPhenotypicFeatureAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene_id,
    predicate="biolink:has_phenotype",
    object=phenotype_id,
    aggregating_knowledge_source="infores:monarchinitiative",
    primary_knowledge_source="infores:hpoa",
    qualifiers=qualifiers,
    has_evidence=evidence
)

koza_app.write(association)
