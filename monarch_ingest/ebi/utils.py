"""
Utility methods for EBI ingests
"""
import uuid
from koza.cli_runner import koza_app

#
# Gene to Phenotype Ingest utility methods
#

#
# TODO: how do we handle this: the Biolink Model only has
#       the predicate "has molecular consequence",
#       without any exact mapping nor relation mapping defined?
#
# def get_consequence_predicate(consequence):
#     #
#     # Original Dipper map (based on original G2P terms?).
#     # TODO: Note that the original list is orthogonal, but the new mapping is not,
#     #       hence there now is an overlap between the two consequence types?
#     #
#     # consequence_map = {
#     #     'has_molecular_consequence': [
#     #         '5_prime or 3_prime UTR mutation',
#     #         'all missense/in frame',
#     #         'cis-regulatory or promotor mutation',
#     #         'part of contiguous gene duplication'
#     #     ],
#     #     'has_functional_consequence': [
#     #         'activating',
#     #         'dominant negative',
#     #         'increased gene dosage',
#     #         'loss of function'
#     #     ]
#     # }
#     consequence_map = {
#         'has_molecular_consequence': [
#             '5_prime or 3_prime UTR mutation',
#             'altered gene product structure',  # 'all missense/in frame',
#             'cis-regulatory or promotor mutation',
#             'increased gene product level'  # 'part of contiguous gene duplication'
#         ],
#         'has_functional_consequence': [
#             'altered gene product structure',  # 'activating'
#             'altered gene product structure',  # 'dominant negative'
#             'increased gene product level',  # 'increased gene dosage'
#             'absent gene product'  # 'loss of function'
#         ]
#     }
#     consequence_type = 'uncertain'
#     for typ, typ_list in consequence_map.items():
#         if consequence in typ_list:
#             consequence_type = typ
#
#     return consequence_type

#
# Extracted from Alliance gene_to_phenotype code
#
# # TODO: another exemplar for EBI - needs fixing
# gene_ids = koza_app.get_map("alliance-gene")
#
# if len(row["phenotypeTermIdentifiers"]) == 0:
#     LOG.warning("Phenotype ingest record has 0 phenotype terms: " + str(row))
#
# if len(row["phenotypeTermIdentifiers"]) > 1:
#     LOG.warning("Phenotype ingest record has >1 phenotype terms: " + str(row))
#
# # limit to only genes
# if row["objectId"] in gene_ids.keys() and len(row["phenotypeTermIdentifiers"]) == 1:
#
#     source = source_map[row["objectId"].split(':')[0]]
#
#     pheno_id = row["phenotypeTermIdentifiers"][0]["termId"]
#     # Remove the extra WB: prefix if necessary
#     pheno_id = pheno_id.replace("WB:WBPhenotype:", "WBPhenotype:")
#
#     gene = Gene(id=row["objectId"], source=source)
#
#     # populate any additional optional gene properties
#     if row['xrefs']:
#         gene.xrefs = [curie_cleaner.clean(xref) for xref in row['xrefs']]
#
#     phenotypicFeature = PhenotypicFeature(id=pheno_id, source=source)
#     association = GeneToPhenotypicFeatureAssociation(
#         id="uuid:" + str(uuid.uuid1()),
#         subject=gene.id,
#         predicate=Predicate.has_phenotype,
#         object=phenotypicFeature.id,
#         relation=koza_app.translation_table.resolve_term("has phenotype"),
#         publications=[row["evidence"]["publicationId"]],
#         source=source,
#     )
#
#     if "conditionRelations" in row.keys() and row["conditionRelations"] is not None:
#         qualifiers = []
#         for conditionRelation in row["conditionRelations"]:
#             for condition in conditionRelation["conditions"]:
#                 if condition["conditionClassId"]:
#                     qualifiers.append(condition["conditionClassId"])
#         association.qualifiers = qualifiers
#
#     koza_app.write(association)

#
# extracted from Dipper implementation
# dipper/sources/EBIGene2Phen.py::_build_gene_disease_model()
#
"""
Parsing of each row of the gene-to-phenotype file.

We create anonymous variants along with their attributes
(allelic requirement, functional consequence)
and connect these to genes and diseases.

Genes are associated with variants via global_terms['has_affected_locus'].

Variants are associated with their attributes via:
- global_terms['has_allelic_requirement']
- global_terms['has_functional_consequence']

Variants are connected to disease based on mappings to the DDD category column,

See the translation table specific to this source for mappings.

For cases where there are no disease OMIM id,
we either use a disease cache file with mappings
to MONDO that has been manually curated.

"""

# TODO: temporary hack to silence compile errors
model = None
geno = None


def publish_gene_variant_disease_phenotype_statements(
        gene_id,
        gene_to_disease_predicate,
        disease_id,
        variant_label,
        consequence_predicate,
        consequence_id,
        allelic_requirement,
        publications
):
    """
    Publishes gene-variant-disease predicate statement
    """
    is_variant = False
    variant_or_gene = gene_id

    variant_id_string = variant_label
    variant_bnode = str(f"{variant_id_string}_{uuid.uuid1()}")  # self.make_id(variant_id_string, "_")

    # TODO: we don't really model blank nodes in KGX.
    #       Perhaps this information needs to be embedded in the _attributes JSON blob?
    #       Or do we need to add an additional predicate statement?
    if consequence_predicate and consequence_id:
        is_variant = True
        model.addTriple(
            variant_bnode,
            consequence_predicate,
            consequence_id
        )
        # Hack to add labels to terms that don't exist in an ontology
        if consequence_id.startswith(':'):
            model.addLabel(
                consequence_id,
                consequence_id.strip(':').replace('_', ' ')
            )

    if is_variant:
        # TODO: if we have a mutation consequence, then we model a variant association?
        variant_or_gene = variant_bnode
        # We would typically type the variant using the
        # molecular consequence, but these are not specific
        # enough for us to make mappings (see translation table)
        model.addIndividualToGraph(
            variant_bnode,
            variant_label,

            # this is the 'relation' slot value, not the predicate?
            koza_app.translation_table.resolve_term('variant_locus')
        )
        geno.addAffectedLocus(variant_bnode, gene_id)
        model.addBlankNodeAnnotation(variant_bnode)

    # the main event here is the gene-to-disease association?
    # TODO: temporary hack to silence compile errors
    assoc = None  # G2PAssoc(variant_or_gene, disease_id, gene_to_disease_predicate)

    assoc.source = publications
    assoc.add_association_to_graph()

    if allelic_requirement is not None and is_variant is False:
        model.addTriple(
            assoc.assoc_id,
            koza_app.translation_table.resolve_term('has_allelic_requirement'),
            allelic_requirement
        )
        if allelic_requirement.startswith(':'):
            model.addLabel(
                allelic_requirement,
                allelic_requirement.strip(':').replace('_', ' ')
            )
