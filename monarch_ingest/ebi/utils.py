"""
Utility methods for EBI ingests
"""
from koza.cli_runner import koza_app

#
# Gene to Phenotype Ingest utility methods
#

#
# extracted from Dipper implementation
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
mondo_map = koza_app.get_map('mondo_map')


def build_gene_disease_model(
        self,
        gene_id,
        relation_id,
        disease_id,
        variant_label,
        consequence_predicate=None,
        consequence_id=None,
        allelic_requirement=None,
        pmids=None):
    """
    Builds gene variant disease model
    :return: None
    """
    model = Model(self.graph)
    geno = Genotype(self.graph)

    pmids = [] if pmids is None else pmids

    is_variant = False
    variant_or_gene = gene_id

    variant_id_string = variant_label
    variant_bnode = self.make_id(variant_id_string, "_")

    if consequence_predicate is not None \
            and consequence_id is not None:
        is_variant = True
        model.addTriple(variant_bnode,
                        consequence_predicate,
                        consequence_id)
        # Hack to add labels to terms that
        # don't exist in an ontology
        if consequence_id.startswith(':'):
            model.addLabel(consequence_id,
                           consequence_id.strip(':').replace('_', ' '))

    if is_variant:
        variant_or_gene = variant_bnode
        # Typically we would type the variant using the
        # molecular consequence, but these are not specific
        # enough for us to make mappings (see translation table)
        model.addIndividualToGraph(variant_bnode,
                                   variant_label,
                                   self.globaltt['variant_locus'])
        geno.addAffectedLocus(variant_bnode, gene_id)
        model.addBlankNodeAnnotation(variant_bnode)

    assoc = G2PAssoc(
        self.graph, self.name, variant_or_gene, disease_id, relation_id)
    assoc.source = pmids
    assoc.add_association_to_graph()

    if allelic_requirement is not None and is_variant is False:
        model.addTriple(
            assoc.assoc_id, self.globaltt['has_allelic_requirement'],
            allelic_requirement)
        if allelic_requirement.startswith(':'):
            model.addLabel(
                allelic_requirement,
                allelic_requirement.strip(':').replace('_', ' '))


def get_consequence_predicate(consequence):
    #
    # Original Dipper map (based on original G2P terms?).
    # TODO: Note that the original list is orthogonal, but the new mapping is not,
    #       hence there now is an overlap between the two consequence types?
    #
    # consequence_map = {
    #     'has_molecular_consequence': [
    #         '5_prime or 3_prime UTR mutation',
    #         'all missense/in frame',
    #         'cis-regulatory or promotor mutation',
    #         'part of contiguous gene duplication'
    #     ],
    #     'has_functional_consequence': [
    #         'activating',
    #         'dominant negative',
    #         'increased gene dosage',
    #         'loss of function'
    #     ]
    # }
    consequence_map = {
        'has_molecular_consequence': [
            '5_prime or 3_prime UTR mutation',
            'altered gene product structure',
            'cis-regulatory or promotor mutation',
            'increased gene product level'
        ],
        'has_functional_consequence': [
            'altered gene product structure',
            'altered gene product structure',
            'increased gene product level',
            'absent gene product'
        ]
    }
    consequence_type = 'uncertain'
    for typ, typ_list in consequence_map.items():
        if consequence in typ_list:
            consequence_type = typ

    return consequence_type


def process_gene_disease(row):  # ::List  getting syntax error here
    """
    Parse and add gene variant disease model
    Model building happens in build_gene_disease_model
    
    :param row:  single row from EBI G2P csv input file.

    """
    variant_label = "variant of {}".format(row['gene_symbol'])
    disease_omim_id = row['disease_omim_id']
    if disease_omim_id == 'No disease mim':
        # check if we've manually curated
        disease_label = row['disease_label']
        if disease_label in mondo_map:
            disease_id = mondo_map['disease_label']
        else:
            return  # sorry for this
    else:
        disease_id = 'OMIM:' + disease_omim_id

    hgnc_curie = 'HGNC:' + row['hgnc_id']

    relation_curie = koza_app.translation_table.local_tablerow['g2p_relation_label']
    mutation_consequence = row['mutation_consequence']
    if mutation_consequence not in ('uncertain', ''):
        consequence_relation = koza_app.translation_table.local_table[
            get_consequence_predicate(mutation_consequence)]
        consequence_curie = koza_app.translation_table.local_table[mutation_consequence]
        variant_label = "{} {}".format(mutation_consequence, variant_label)
    else:
        consequence_relation = None
        consequence_curie = None

    allelic_requirement = row['allelic_requirement']
    if allelic_requirement != '':
        requirement_curie = koza_app.translation_table.local_table[allelic_requirement]
    else:
        requirement_curie = None

    pmids = row['pmids']
    if pmids != '':
        pmid_list = ['PMID:' + pmid for pmid in pmids.split(';')]
    else:
        pmid_list = []

    # build the model
    # Should we build a reusable object and/or tuple that
    # could be passed to a more general model builder for
    # this and orphanet (and maybe clinvar)
    build_gene_disease_model(
        hgnc_curie,
        relation_curie,
        disease_id,
        variant_label,
        consequence_relation,
        consequence_curie,
        requirement_curie,
        pmid_list
    )
