import uuid

from koza.cli_runner import koza_app

from biolink.pydanticmodel import ChemicalToPathwayAssociation

source_name = "reactome_gene_to_pathway"

row = koza_app.get_row(source_name)

gene_id = "ENSEMBL:" + row["component"]

pathway_id = "REACT:" + row["pathway_id"]

association = ChemicalToPathwayAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene_id,
    predicate="biolink:participates_in",
    object=pathway_id,
    aggregator_knowledge_source=["infores:monarchinitiative"],
    primary_knowledge_source="infores:reactome",
)

koza_app.write(association)
