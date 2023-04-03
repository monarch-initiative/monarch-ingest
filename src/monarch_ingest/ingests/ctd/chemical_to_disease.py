import uuid

from koza.cli_runner import get_koza_app

from biolink.pydanticmodel import ChemicalToDiseaseOrPhenotypicFeatureAssociation

koza_app = get_koza_app("ctd_chemical_to_disease")

while (row := koza_app.get_row()) is not None:

    if row['DirectEvidence'] in ['therapeutic']:

        chemical_id = 'MESH:' + row['ChemicalID']

        disease_id = row['DiseaseID']

        # Update this if we start bringing in marker/mechanism records
        predicate = "biolink:treats"
        relation = koza_app.translation_table.resolve_term("is substance that treats")

        association = ChemicalToDiseaseOrPhenotypicFeatureAssociation(
            id="uuid:" + str(uuid.uuid1()),
            subject=chemical_id,
            predicate=predicate,
            object=disease_id,
            publications=["PMID:" + p for p in row['PubMedIDs'].split("|")],
            aggregator_knowledge_source=["infores:monarchinitiative"],
            primary_knowledge_source="infores:ctd"
        )

        koza_app.write(association)
