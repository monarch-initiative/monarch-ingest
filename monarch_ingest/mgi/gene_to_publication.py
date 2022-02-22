import uuid

from biolink_model_pydantic.model import (
    Gene,
    NamedThingToInformationContentEntityAssociation,
    Predicate,
    Publication,
)
from koza.cli_runner import koza_app

source_name = "mgi_gene_to_publication"

row = koza_app.get_row(source_name)

gene = Gene(
    id=row["MGI Marker Accession ID"],
    source="infores:mgi",
    type=koza_app.translation_table.resolve_term("gene"),
)

pub_ids = row["PubMed IDs"].split("|")
pubs = []
for pub_id in pub_ids:
    pmid = "PMID:" + pub_id
    pubs.append(
        Publication(
            id=pmid,
            type=koza_app.translation_table.resolve_term("publication"),
            source="infores:mgi",
        )
    )

    association = NamedThingToInformationContentEntityAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene.id,
        predicate=Predicate.mentions,
        object=pmid,
        relation=koza_app.translation_table.resolve_term("mentions"),
        source="infores:mgi",
    )

for pub in pubs:
    koza_app.write(gene, pub, association)  # , row_limit=5)
