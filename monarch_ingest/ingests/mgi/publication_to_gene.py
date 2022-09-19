import uuid

from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import InformationContentEntityToNamedThingAssociation

koza_app = get_koza_app("mgi_publication_to_gene")

row = koza_app.get_row()

gene_id=row["MGI Marker Accession ID"]

relation = koza_app.translation_table.resolve_term("mentions")

pub_ids = row["PubMed IDs"].split("|")

for pub_id in pub_ids:

    pmid = "PMID:" + pub_id

    association = InformationContentEntityToNamedThingAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=pmid,
        predicate="biolink:mentions",
        object=gene_id,
        aggregator_knowledge_source=["infores:monarchinitiative"],
        primary_knowledge_source="infores:mgi"
    )

    koza_app.write(association)
