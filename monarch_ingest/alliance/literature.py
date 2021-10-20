from biolink_model_pydantic.model import Publication
from koza.cli_runner import koza_app

source_name = "literature"

row = koza_app.get_row(source_name)


# TODO: remove DOI exclusion once curie regex can handle them
xrefs = [xref["id"] for xref in row["crossReferences"] if not xref["id"].startswith("DOI:")]

pub = Publication(
    id=row["primaryId"],
    name=row["title"],
    summary=row["abstract"] if "abstract" in row.keys() else None,
    xref=xrefs,
    type=koza_app.translation_table.resolve_term("publication"),
    creation_date=row["datePublished"],
)

if "authors" in row.keys():
    pub.authors = ", ".join([author["name"] for author in row["authors"]])

if "meshTerms" in row.keys():
    pub.mesh_terms = []
    pub.mesh_terms += [term.get("meshQualifierTerm") for term in row["meshTerms"] if term.get("meshQualifierTerm")]
    pub.mesh_terms += [term.get("meshHeadingTerm") for term in row["meshTerms"] if term.get("meshHeadingTerm")]

if "keywords" in row.keys():
    pub.keywords = row["keywords"]

if row["allianceCategory"] in ["Preprint", "Research Article", "Review Article"]:
    pub.type = koza_app.translation_table.resolve_term("journal article")

koza_app.write(pub)
