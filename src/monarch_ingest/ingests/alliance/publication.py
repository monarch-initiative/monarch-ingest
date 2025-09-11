from koza.cli_utils import get_koza_app
from dateutil.parser import parse, ParserError

from biolink_model.datamodel.pydanticmodel_v2 import Publication
from source_translation import source_map

koza_app = get_koza_app("alliance_publication")

while (row := koza_app.get_row()) is not None:

    # TODO: remove DOI exclusion once curie regex can handle them
    xrefs = [xref["id"] for xref in row["crossReferences"] if not xref["id"].startswith("DOI:")]

    # Parse creation date for different time formats
    creation_date = row["datePublished"]
    try:
        creation_date = parse(creation_date)
    except (ParserError, OverflowError):
        creation_date = None

    source: str
    if (
        'MODReferenceTypes' in row
        and len(row['MODReferenceTypes']) > 0
        and 'source' in row['MODReferenceTypes'][0]
        and row['MODReferenceTypes'][0]['source'] in source_map
    ):
        source = source_map[row['MODReferenceTypes'][0]['source']]
    else:  # default source
        source = "infores:agrkb"

    pub = Publication(
        id=row["primaryId"],
        name=row["title"],
        summary=row["abstract"] if "abstract" in row.keys() else None,
        xref=xrefs,
        type=[koza_app.translation_table.resolve_term("publication")],
        creation_date=creation_date,
        provided_by=[source],
    )

    if "authors" in row.keys():
        pub.authors = [author["name"] for author in row["authors"]]

    if "meshTerms" in row.keys():
        mesh_terms = []
        for term in row["meshTerms"]:
            # yes, meshQualifierTerm is spelled as meshQualfierTerm
            if term.get("meshQualfierTerm"):
                mesh_terms.append("MESH:" + term.get("meshQualfierTerm"))
            # include support for the correct spelling, so this keeps working once it's fixed upstream
            if term.get("meshQualifierTerm"):
                mesh_terms.append("MESH:" + term.get("meshQualifierTerm"))
            if term.get("meshHeadingTerm"):
                mesh_terms.append("MESH:" + term.get("meshHeadingTerm"))
        pub.mesh_terms = list(set(mesh_terms))  # Make the list unique

    if "keywords" in row.keys():
        pub.keywords = row["keywords"]

    if row["allianceCategory"] in ["Preprint", "Research Article", "Review Article"]:
        pub.type = [koza_app.translation_table.resolve_term("journal article")]

    koza_app.write(pub)
