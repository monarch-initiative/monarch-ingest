import uuid

from koza.cli_runner import koza_app

from model.biolink import (
    ChemicalEntity,
    ChemicalToDiseaseOrPhenotypicFeatureAssociation,
    Disease,
)

source_name = "ctd_chemical_to_disease"

row = koza_app.get_row(source_name)

if row['DirectEvidence'] in ['therapeutic']:

    chemical = ChemicalEntity(
        id='MESH:' + row['ChemicalID'], name=row['ChemicalName'], source='infores:ctd'
    )

    disease = Disease(id=row['DiseaseID'], source="infores:ctd")

    # Update this if we start bringing in marker/mechanism records
    predicate = "biolink:treats"
    relation = koza_app.translation_table.resolve_term("is substance that treats")

    association = ChemicalToDiseaseOrPhenotypicFeatureAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=chemical.id,
        predicate=predicate,
        object=disease.id,
        #relation=relation,
        publications=["PMID:" + p for p in row['PubMedIDs'].split("|")],
        source="infores:ctd",
    )

    koza_app.write(association)
