import uuid
#from biolink_model_pydantic.model import (Gene,InformationContentEntityToNamedThingAssociation,Predicate,Publication)
from model.biolink import Gene, InformationContentEntityToNamedThingAssociation, Publication
from koza.cli_runner import koza_app

source_name = "mgi_publication_to_gene"

row = koza_app.get_row(source_name)

gene = Gene(
    id=row["MGI Marker Accession ID"],
    source="infores:mgi",
    type=koza_app.translation_table.resolve_term("gene"),
)

pub_ids = row["PubMed IDs"].split("|")
for pub_id in pub_ids:
    pmid = "PMID:" + pub_id
    pub = Publication(
        id=pmid,
        type=koza_app.translation_table.resolve_term("publication"),
        source="infores:mgi",
    )

    association = InformationContentEntityToNamedThingAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=pmid,
        predicate="biolink:mentions",
        object=gene.id,
        relation=koza_app.translation_table.resolve_term("mentions"),
        source="infores:mgi",
    )

    koza_app.write(association)
