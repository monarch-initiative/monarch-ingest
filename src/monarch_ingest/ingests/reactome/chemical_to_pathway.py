import uuid
import koza
from biolink_model.datamodel.pydanticmodel_v2 import ChemicalToPathwayAssociation, AgentTypeEnum, KnowledgeLevelEnum


@koza.transform_record()
def transform_record(koza_transform, row):
    species = row["species_nam"]

    # Inline species mapping from reactome_id_mapping.yaml
    # TODO: Re-implement local_table lookup when mapping file structure is clarified
    species_mapping = {
        "Homo sapiens": "NCBITaxon:9606",
        "Canis familiaris": "NCBITaxon:9615",
        "Bos taurus": "NCBITaxon:9913",
        "Sus scrofa": "NCBITaxon:9823",
        "Rattus norvegicus": "NCBITaxon:10116",
        "Mus musculus": "NCBITaxon:10090",
        "Gallus gallus": "NCBITaxon:9031",
        "Xenopus tropicalis": "NCBITaxon:8364",
        "Danio rerio": "NCBITaxon:7955",
        "Drosophila melanogaster": "NCBITaxon:7227",
        "Caenorhabditis elegans": "NCBITaxon:6239",
        "Dictyostelium discoideum": "NCBITaxon:44689",
        "Schizosaccharomyces pombe": "NCBITaxon:4896",
        "Saccharomyces cerevisiae": "NCBITaxon:4932",
    }

    # Skip if species not in our mapping
    if species not in species_mapping:
        return []

    taxon_id = species_mapping[species]

    chemical_id = "CHEBI:" + row["component"]
    pathway_id = "Reactome:" + row["pathway_id"]  # pathways themselves are an independent ingest now...

    go_evidence_code = row["go_ecode"]
    # TODO: Re-implement translation_table.resolve_term when global table is clarified
    # For now, inline common GO evidence code mappings
    evidence_mapping = {
        "IEA": "ECO:0000501",  # inferred from electronic annotation
        "TAS": "ECO:0000304",  # traceable author statement
        "IC": "ECO:0000305",  # inferred by curator
        "IDA": "ECO:0000314",  # direct assay
        "IMP": "ECO:0000315",  # mutant phenotype
    }
    evidence_code_term = evidence_mapping.get(go_evidence_code, go_evidence_code)

    association = ChemicalToPathwayAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=chemical_id,
        predicate="biolink:participates_in",
        object=pathway_id,
        has_evidence=[evidence_code_term],
        aggregator_knowledge_source=["infores:monarchinitiative"],
        primary_knowledge_source="infores:reactome",
        knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
        agent_type=AgentTypeEnum.not_provided,
    )

    return [association]
