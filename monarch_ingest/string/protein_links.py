import re
import uuid

from biolink_model_pydantic.model import PairwiseGeneToGeneInteraction, Predicate, Protein

from koza.cli_runner import koza_app

row = koza_app.get_row()

# TODO: how are we going to map any protein node properties to 'Gene' and
#       would we include 'in_taxon' values rather than deleting them here?
#   - 'id'
#   - 'category'
#   x - 'provided_by'  # not emphasized in Biolink
#   x - 'name'
#   x - 'symbol'
#   - 'in_taxon'
#   x - 'xref'
#   x - 'synonym'
#   - 'source'  # is this still needed?
pid_a = row['protein1']
ens_a = 'ENSEMBL:' + re.sub(r'\d+\.', '', pid_a)
ncbitaxon_match_a = re.match(r'\d+', pid_a)
if ncbitaxon_match_a:
    ncbitaxon_a = "NCBITaxon:" + ncbitaxon_match_a.group(0)
    protein_a = Protein(id=ens_a, in_taxon=ncbitaxon_a, source="ENSEMBL")
else:
    protein_a = Protein(id=ens_a, source="ENSEMBL")

pid_b = row['protein2']
ens_b = 'ENSEMBL:' + re.sub(r'\d+\.', '', pid_b)
ncbitaxon_match_b = re.match(r'\d+', pid_b)
if ncbitaxon_match_b:
    ncbitaxon_b = "NCBITaxon:" + ncbitaxon_match_b.group(0)
    protein_b = Protein(id=ens_b, in_taxon=ncbitaxon_b, source="ENSEMBL")
else:
    protein_b = Protein(id=ens_b, source="ENSEMBL")

pairwise_gene_to_gene_interaction = PairwiseGeneToGeneInteraction(
    id="uuid:" + str(uuid.uuid1()),
    subject=protein_a.id,
    object=protein_b.id,
    predicate=Predicate.interacts_with,
    relation=koza_app.translation_table.global_table['interacts with'],
    provided_by="infores:string"
)

koza_app.write(protein_a, protein_b, pairwise_gene_to_gene_interaction)
