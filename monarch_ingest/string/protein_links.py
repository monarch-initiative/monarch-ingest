import re
import uuid

from biolink_model_pydantic.model import Gene, PairwiseGeneToGeneInteraction, Predicate
from koza.cli_runner import koza_app

row = koza_app.get_row()
entrez_2_string = koza_app.get_map('entrez_2_string')

pid_a = row['protein1']
gene_ids_a = entrez_2_string[pid_a]['entrez']
pid_b = row['protein2']
gene_ids_b = entrez_2_string[pid_b]['entrez']

# Some genes may not be found in the mapping, only process the record if both are found
if gene_ids_a and gene_ids_b:

    entities = []

    for gid_a in gene_ids_a.split("|"):
        for gid_b in gene_ids_b.split("|"):
            gid_a = 'NCBIGene:' + gid_a
            gid_b = 'NCBIGene:' + gid_b

            ncbitaxon_match_a = re.match(r'\d+', pid_a)
            if ncbitaxon_match_a:
                ncbitaxon_a = "NCBITaxon:" + ncbitaxon_match_a.group(0)
                gene_a = Gene(id=gid_a, in_taxon=ncbitaxon_a, source="infores:entrez")
            else:
                gene_a = Gene(id=gid_a, source="entrez")

            ncbitaxon_match_b = re.match(r'\d+', pid_b)
            if ncbitaxon_match_b:
                ncbitaxon_b = "NCBITaxon:" + ncbitaxon_match_b.group(0)
                gene_b = Gene(id=gid_b, in_taxon=ncbitaxon_b, source="infores:entrez")
            else:
                gene_b = Gene(id=gid_b, source="entrez")

            association = PairwiseGeneToGeneInteraction(
                id="uuid:" + str(uuid.uuid1()),
                subject=gene_a.id,
                object=gene_b.id,
                predicate=Predicate.interacts_with,
                relation=koza_app.translation_table.global_table['interacts with'],
                source="infores:string",
            )

            entities.append(gene_a)
            entities.append(gene_b)
            entities.append(association)

    koza_app.write(*entities)
