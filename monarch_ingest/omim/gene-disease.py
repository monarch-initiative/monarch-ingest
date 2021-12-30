"""
OMIM Gene to Disease Ingest

Usage:
poetry run koza transform \
  --global-table monarch_ingest/translation_table.yaml \
  --local-table monarch_ingest/omim/omim-translation.yaml \
  --source monarch_ingest/omim/gene-disease.yaml \
  --output-format tsv
"""

import logging
import re
import uuid

from biolink_model_pydantic.model import (
    Disease,
    Gene,
    GeneToDiseaseAssociation,
    NucleicAcidEntity,
    Predicate,
)
from koza.cli_runner import koza_app

LOG = logging.getLogger(__name__)


source_name = "omim-gene-disease"
row = koza_app.get_row(source_name)
omim_to_gene = koza_app.get_map('mim2gene')

disorder = row['Phenotype']
gene_symbols = row['Gene Symbols']
gene_num = row['MIM Number']


# These two regexes are used to capture the standard
# case where there is ${disease label}, ${omim id}
# for example:
# 3-M syndrome 1, 273750 (3)|CUL7, 3M1|609577|6p21.1

# The other case are for ids that are used for both
# the disease and genomic loci together
#
# In these cases we treat the NCBIGene xref as the
# nucleic acid entity (phenotypic heritable marker),
# and the OMIM id as the disease entity, for example:
# Alopecia areata 1 (2)|AA1|104000|18p11.3-p11.2

# note that for those diseases where they are genomic loci
# (not genes though), the omim id is only listed as the gene
# when there's a gene and disease
disorder_regex = re.compile(r'(.*), (\d{6})\s*(?:\((\d+)\))?')
no_disease_id_regex = re.compile(r'(.*)\s+\((\d+)\)')

disorder_match = disorder_regex.match(disorder)
no_disease_id_match = no_disease_id_regex.match(disorder)

disorder_id = None
disorder_label = None
association_key = None
gene_id = None

if disorder_match is not None:
    disorder_parts = disorder_match.groups()
    disorder_label, disorder_num, association_key = disorder_parts

    gene_symbols = gene_symbols.split(', ')
    gene_id = 'OMIM:' + str(gene_num)
    disorder_id = 'OMIM:' + disorder_num

    gene = Gene(id=gene_id)
    koza_app.write(gene)

elif no_disease_id_match is not None:
    # this is a case where the disorder
    # a blended gene/phenotype
    # we lookup the NCBIGene feature and make the association
    disorder_label, association_key = no_disease_id_match.groups()
    # make what's in the gene column the disease
    disorder_id = 'OMIM:' + gene_num
    ncbi_id = ''
    if gene_num in omim_to_gene:
        ncbi_id = omim_to_gene[gene_num]['Entrez Gene ID (NCBI)']
    if ncbi_id == '':
        koza_app.next_row()
    gene_id = 'NCBIGene:' + ncbi_id

    genomic_entity = NucleicAcidEntity(
        id=gene_id,
        type=koza_app.translation_table.global_table['heritable_phenotypic_marker'],
    )
    koza_app.write(genomic_entity)

else:
    # In dipper we created anonymous nodes for these cases, but for now we will skip these
    # It doesn't appear that anything falls into this category as of 1/11/2021
    LOG.warning(f"skipped {row}")
    koza_app.next_row()


# From the docs:

# Brackets, "[ ]", indicate "nondiseases," mainly genetic variations
# that lead to apparently abnormal laboratory test values

# (e.g., dysalbuminemic euthyroidal hyperthyroxinemia).
# Braces, "{ }", indicate mutations that contribute to susceptibility
# to multifactorial disorders (e.g., diabetes, asthma) or to
# susceptibility to infection (e.g., malaria).
#
# A question mark, "?", before the phenotype name indicates that the
# relationship between the phenotype and gene is provisional.
# More details about this relationship are provided in the comment
# field of the map and in the gene and phenotype OMIM entries.

# Phene key:
# The number in parentheses after the name of each disorder indicates
# the following:
#   (1) the disorder was positioned by mapping of the wildtype gene;
#   (2) the disease phenotype itself was mapped;
#   (3) the molecular basis of the disorder is known;
#   (4) the disorder is a chromosome deletion or duplication syndrome.
# reference: https://omim.org/help/faq#1_6

predicate = Predicate.gene_associated_with_condition
relation = koza_app.translation_table.global_table['causes condition']

if disorder_label.startswith('['):
    # predicate = Predicate.related_condition
    # relation = koza_app.translation_table.global_table['is marker for']
    koza_app.next_row()
elif disorder_label.startswith('{'):
    # predicate = Predicate.risk_affected_by
    # relation = koza_app.translation_table.global_table['contributes to']
    koza_app.next_row()
elif disorder_label.startswith('?'):
    # this is a questionable mapping!  skip?, skipping for now
    # predicate = Predicate.related_condition
    # relation = koza_app.translation_table.global_table['contributes to']
    koza_app.next_row()


evidence = None
if association_key is not None:
    evidence = koza_app.translation_table.resolve_term(association_key, False)
    if evidence == association_key:
        evidence = None

disease = Disease(
    id=disorder_id,
)

# Association
association = GeneToDiseaseAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=gene_id,
    predicate=predicate,
    object=disorder_id,
    relation=relation,
    has_evidence=evidence,
    source='infores:omim'
)

koza_app.write(disease, association)
