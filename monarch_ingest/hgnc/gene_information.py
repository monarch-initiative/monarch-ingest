import uuid

from biolink_model_pydantic.model import (
    Gene,
    NamedThingToInformationContentEntityAssociation,
    Predicate,
    Publication,
)
from koza.cli_runner import koza_app

source_name = "hgnc_gene_information"

row = koza_app.get_row(source_name)

if not row["pubmed_id"]:
    koza_app.next_row()

xref_list = []
xref_list.append('ENSEMBL:' + row['ensembl_gene_id'])
if '|' in row['omim_id']:
    for each in row['omim_id'].split('|'):
        xref_list.append('OMIM:' + each)
else:
    xref_list.append('OMIM:' + row['omim_id'])


synonyms_list = row["alias_symbol"].split("|") + row["alias_name"].split("|") + \
                row["prev_symbol"].split("|") + row["prev_name"].split("|")

gene = Gene(id=row["hgnc_id"],
            symbol=row["symbol"],
            name=row["name"],
            xref=xref_list,
            synonym=synonyms_list
            )

pubmed_id_list = row["pubmed_id"].split('|')
for each_id in pubmed_id_list:
    publication_id = "PMID:" + each_id
    publication = Publication(
        id=publication_id,
        type=koza_app.translation_table.resolve_term("publication"),
    )
    association = NamedThingToInformationContentEntityAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene.id,
        predicate=Predicate.mentions,
        object=publication.id,
        relation=koza_app.translation_table.resolve_term("mentions"),
    )

    koza_app.write(gene, publication, association)
