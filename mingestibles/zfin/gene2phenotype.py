import logging
import uuid

from biolink_model_pydantic.model import (
    Gene,
    GeneToPhenotypicFeatureAssociation,
    PhenotypicFeature,
    Predicate,
)
from koza.manager.data_collector import write
from koza.manager.data_provider import inject_map, inject_row, inject_translation_table

LOG = logging.getLogger(__name__)

source_name = "gene-to-phenotype"

row = inject_row(source_name)
eqe2zp = inject_map("eqe2zp")
translation_table = inject_translation_table()

if row["Phenotype Tag"] == "abnormal":
    zp_key_elements = [
        row["Affected Structure or Process 1 subterm ID"],
        row["Post-composed Relationship ID"],
        row["Affected Structure or Process 1 superterm ID"],
        row["Phenotype Keyword ID"],
        row["Affected Structure or Process 2 subterm ID"],
        row["Post-composed Relationship (rel) ID"],
        row["Affected Structure or Process 2 superterm ID"],
    ]

    zp_key = "-".join([element or "0" for element in zp_key_elements])

    zp_term = eqe2zp[zp_key]["iri"]

    if not zp_term:
        LOG.warning("ZP concatenation " + zp_key + " did not match a ZP term")

    gene = Gene(id="ZFIN:" + row["Gene ID"])
    phenotypicFeature = PhenotypicFeature(id=zp_term)
    association = GeneToPhenotypicFeatureAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene.id,
        predicate=Predicate.has_phenotype,
        object=phenotypicFeature.id,
        relation=translation_table.resolve_term("has phenotype"),
        publications="ZFIN:" + row["Publication ID"],
    )

    write(source_name, gene, phenotypicFeature, association)
