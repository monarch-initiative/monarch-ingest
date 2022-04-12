import logging
import uuid

from biolink_model_pydantic.model import (
    Gene,
    GeneToPhenotypicFeatureAssociation,
    PhenotypicFeature,
    Predicate,
)

from koza.cli_runner import koza_app

# TODO: Probably not fit-for-purpose... just an exemplar for the EBI ingest?
from monarch_ingest.alliance.source_translation import source_map

LOG = logging.getLogger(__name__)

# You've got 'NCBI_Gene:' and you want 'NCBIGene:'? clean it up.
curie_cleaner = koza_app.curie_cleaner

source_name = "ebi_gene_to_phenotype"

row = koza_app.get_row(source_name)

# TODO: another exemplar for EBI - needs fixing
gene_ids = koza_app.get_map("alliance-gene")

if len(row["phenotypeTermIdentifiers"]) == 0:
    LOG.warning("Phenotype ingest record has 0 phenotype terms: " + str(row))

if len(row["phenotypeTermIdentifiers"]) > 1:
    LOG.warning("Phenotype ingest record has >1 phenotype terms: " + str(row))

# limit to only genes
if row["objectId"] in gene_ids.keys() and len(row["phenotypeTermIdentifiers"]) == 1:

    source = source_map[row["objectId"].split(':')[0]]

    pheno_id = row["phenotypeTermIdentifiers"][0]["termId"]
    # Remove the extra WB: prefix if necessary
    pheno_id = pheno_id.replace("WB:WBPhenotype:", "WBPhenotype:")

    gene = Gene(id=row["objectId"], source=source)

    # populate any additional optional gene properties
    if row['xrefs']:
        gene.xrefs = [curie_cleaner.clean(xref) for xref in row['xrefs']]

    phenotypicFeature = PhenotypicFeature(id=pheno_id, source=source)
    association = GeneToPhenotypicFeatureAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=gene.id,
        predicate=Predicate.has_phenotype,
        object=phenotypicFeature.id,
        relation=koza_app.translation_table.resolve_term("has phenotype"),
        publications=[row["evidence"]["publicationId"]],
        source=source,
    )

    if "conditionRelations" in row.keys() and row["conditionRelations"] is not None:
        qualifiers = []
        for conditionRelation in row["conditionRelations"]:
            for condition in conditionRelation["conditions"]:
                if condition["conditionClassId"]:
                    qualifiers.append(condition["conditionClassId"])
        association.qualifiers = qualifiers

    koza_app.write(association)

#
# Dipper implementation
#
#      def parse(self, limit: Optional[int]=None):
#         """
#         Here we parse each row of the gene-to-phenotype file.
#
#         We create anonymous variants along with their attributes
#         (allelic requirement, functional consequence)
#         and connect these to genes and diseases.
#
#         Genes are associated with variants via global_terms['has_affected_locus'].

#         Variants are associated with their attributes via:
#         - global_terms['has_allelic_requirement']
#         - global_terms['has_functional_consequence']

#         Variants are connected to disease based on mappings to the DDD category column,

#         See the translation table specific to this source for mappings.

#         For cases where there are no disease OMIM id,
#         we either use a disease cache file with mappings
#         to MONDO that has been manually curated.

#         """
#         if limit is not None:
#             LOG.info("Only parsing first %d rows", limit)
#
#         LOG.info("Parsing files...")
#         file_path = '/'.join((
#             self.rawdir, self.files['developmental_disorders']['file']))
#
#         with gzip.open(file_path, 'rt') as csvfile:
#             reader = csv.reader(csvfile)
#             next(reader)  # header
#             for row in reader:
#                 if limit is None or reader.line_num <= (limit + 1):
#                     self._add_gene_disease(row)
#                 else:
#                     break
#
#         LOG.info("Done parsing.")
#
#     def _add_gene_disease(self, row):  # ::List  getting syntax error here
#         """
#         Parse and add gene variant disease model
#         Model building happens in _build_gene_disease_model
#         :param row {List}: single row from DDG2P.csv
#         :return: None
#         """
#         col = self.files['developmental_disorders']['columns']
#         if len(row) != len(col):
#             raise ValueError("Unexpected number of fields for row {}".format(row))
#
#         variant_label = "variant of {}".format(row[col.index('gene_symbol')])
#         disease_omim_id = row[col.index('disease_omim_id')]
#         if disease_omim_id == 'No disease mim':
#             # check if we've manually curated
#             disease_label = row[col.index('disease_label')]
#             if disease_label in self.mondo_map:
#                 disease_id = self.mondo_map[disease_label]
#             else:
#                 return  # sorry for this
#         else:
#             disease_id = 'OMIM:' + disease_omim_id
#
#         hgnc_curie = 'HGNC:' + row[col.index('hgnc_id')]
#
#         relation_curie = self.resolve(row[col.index('g2p_relation_label')])
#         mutation_consequence = row[col.index('mutation_consequence')]
#         if mutation_consequence not in ('uncertain', ''):
#             consequence_relation = self.resolve(
#                 self._get_consequence_predicate(mutation_consequence))
#             consequence_curie = self.resolve(mutation_consequence)
#             variant_label = "{} {}".format(mutation_consequence, variant_label)
#         else:
#             consequence_relation = None
#             consequence_curie = None
#
#         allelic_requirement = row[col.index('allelic_requirement')]
#         if allelic_requirement != '':
#             requirement_curie = self.resolve(allelic_requirement)
#         else:
#             requirement_curie = None
#
#         pmids = row[col.index('pmids')]
#         if pmids != '':
#             pmid_list = ['PMID:' + pmid for pmid in pmids.split(';')]
#         else:
#             pmid_list = []
#
#         # build the model
#         # Should we build a reusable object and/or tuple that
#         # could be passed to a more general model builder for
#         # this and orphanet (and maybe clinvar)
#         self._build_gene_disease_model(
#             hgnc_curie,
#             relation_curie,
#             disease_id,
#             variant_label,
#             consequence_relation,
#             consequence_curie,
#             requirement_curie,
#             pmid_list
#         )
#
#     def _build_gene_disease_model(
#             self,
#             gene_id,
#             relation_id,
#             disease_id,
#             variant_label,
#             consequence_predicate=None,
#             consequence_id=None,
#             allelic_requirement=None,
#             pmids=None):
#         """
#         Builds gene variant disease model
#         :return: None
#         """
#         model = Model(self.graph)
#         geno = Genotype(self.graph)
#
#         pmids = [] if pmids is None else pmids
#
#         is_variant = False
#         variant_or_gene = gene_id
#
#         variant_id_string = variant_label
#         variant_bnode = self.make_id(variant_id_string, "_")
#
#         if consequence_predicate is not None \
#                 and consequence_id is not None:
#             is_variant = True
#             model.addTriple(variant_bnode,
#                             consequence_predicate,
#                             consequence_id)
#             # Hack to add labels to terms that
#             # don't exist in an ontology
#             if consequence_id.startswith(':'):
#                 model.addLabel(consequence_id,
#                                consequence_id.strip(':').replace('_', ' '))
#
#         if is_variant:
#             variant_or_gene = variant_bnode
#             # Typically we would type the variant using the
#             # molecular consequence, but these are not specific
#             # enough for us to make mappings (see translation table)
#             model.addIndividualToGraph(variant_bnode,
#                                        variant_label,
#                                        self.globaltt['variant_locus'])
#             geno.addAffectedLocus(variant_bnode, gene_id)
#             model.addBlankNodeAnnotation(variant_bnode)
#
#         assoc = G2PAssoc(
#             self.graph, self.name, variant_or_gene, disease_id, relation_id)
#         assoc.source = pmids
#         assoc.add_association_to_graph()
#
#         if allelic_requirement is not None and is_variant is False:
#             model.addTriple(
#                 assoc.assoc_id, self.globaltt['has_allelic_requirement'],
#                 allelic_requirement)
#             if allelic_requirement.startswith(':'):
#                 model.addLabel(
#                     allelic_requirement,
#                     allelic_requirement.strip(':').replace('_', ' '))
#

