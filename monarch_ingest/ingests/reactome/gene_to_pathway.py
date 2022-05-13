import uuid

from koza.cli_runner import koza_app

from model.biolink import ChemicalToPathwayAssociation, Gene, Pathway

source_name = "reactome_gene_to_pathway"

row = koza_app.get_row(source_name)


gene = Gene(id='ENSEMBL:' + row["component"], source="infores:reactome")

pathway = Pathway(
    id="REACT:" + row["pathway_id"],
    type=koza_app.translation_table.resolve_term("pathway"),
    source="infores:reactome",
)

#relation = koza_app.translation_table.resolve_term("participates_in")
association = ChemicalToPathwayAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene.id,
    predicate="biolink:participates_in",
    object=pathway.id,
    source="infores:reactome",
)

koza_app.write(association)
