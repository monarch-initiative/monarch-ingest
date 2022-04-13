import logging
import uuid

from biolink_model_pydantic.model import (
    Gene,
    GeneToDiseaseAssociation,
    GeneToPhenotypicFeatureAssociation,
    PhenotypicFeature,
    Predicate,
)

from koza.cli_runner import koza_app

LOG = logging.getLogger(__name__)

source_name = "ebi_gene_to_phenotype"

row = koza_app.get_row(source_name)

source = "infores:ebi_g2p"

mondo_map = koza_app.get_map('mondo_map')

disease_id = None

disease_omim_id = row['disease_omim_id']
if disease_omim_id == 'No disease mim':
    # check if we've manually curated
    disease_label = row['disease_label']
    if disease_label in mondo_map:
        disease_id = mondo_map['disease_label']
else:
    disease_id = 'OMIM:' + disease_omim_id

if disease_id is not None:

    gene_id = 'HGNC:' + row['hgnc_id']

    variant_label = "variant of {}".format(row['gene_symbol'])

    gene_to_disease_predicate = koza_app.translation_table.local_table["g2p_predicate_label"]

    mutation_consequence = row['mutation_consequence']
    if mutation_consequence not in ('uncertain', ''):
        # TODO: see commented out function "get_consequence_predicate" in monarch_ingest.ebi.utils
        # consequence_relation = koza_app.translation_table.local_table[
        #     get_consequence_predicate(mutation_consequence)
        # ]
        consequence_predicate = "has molecular consequence"
        consequence_id = koza_app.translation_table.local_table[mutation_consequence]
        variant_label = "{} {}".format(mutation_consequence, variant_label)
    else:
        consequence_predicate = None
        consequence_id = None

    allelic_requirement = row['allelic_requirement']
    if allelic_requirement != '':
        allelic_requirement_id = koza_app.translation_table.local_table[allelic_requirement]
    else:
        allelic_requirement_id = None

    pmids = row['pmids']
    if pmids != '':
        publications = ['PMID:' + pmid for pmid in pmids.split(';')]
    else:
        publications = []

    g2d_association = GeneToDiseaseAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene_id,
        predicate=Predicate.gene_associated_with_condition,
        object=disease_id,
        relation=koza_app.translation_table.resolve_term("gene_associated_with_condition"),
        publications=publications,
        source=source,
    )

    koza_app.write(g2d_association)

    # g2p_association = GeneToPhenotypicFeatureAssociation(
    #         id="uuid:" + str(uuid.uuid1()),
    #         subject=gene_id,
    #         predicate=Predicate.has_phenotype,
    #         object=phenotypicFeature_id,
    #         relation=koza_app.translation_table.resolve_term("has phenotype"),
    #         publications=publications,
    #         source=source,
    #     )
    #
    # koza_app.write(g2p_association)

    # # Build the knowledge subgraph
    # publish_gene_variant_disease_phenotype_statements(
    #     gene_id,
    #     gene_to_disease_predicate,
    #     disease_id,
    #     variant_label,
    #     consequence_predicate,
    #     consequence_id,
    #     allelic_requirement_id,
    #     publications
    # )
