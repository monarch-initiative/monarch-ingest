"""
Ingest of Reference Genome Orthologs from Panther
"""
import uuid

from koza.cli_runner import koza_app
from biolink_model_pydantic.model import Gene, Predicate, GeneToGeneHomologyAssociation
from monarch_ingest.orthology.orthology_utils import parse_gene


row = koza_app.get_row()

uniprot_2_gene = koza_app.get_map('uniprot_2_gene')

species_and_gene_id = parse_gene(row['Gene'], uniprot_2_gene)
if species_and_gene_id:
    
    # unpack the species and gene id
    gene_ncbitaxon, gene_id = species_and_gene_id

    species_and_ortholog_id = parse_gene(row['Ortholog'], uniprot_2_gene)
    if species_and_ortholog_id:
        
        # unpack the orthogous gene id and its species
        ortholog_ncbitaxon, ortholog_id = species_and_ortholog_id

        # TODO: how do I discriminate between LDO and O?
        # ortholog_type = row["Type of ortholog"]
        predicate = Predicate.orthologous_to
        relation = koza_app.translation_table.global_table['in orthology relationship with']

        # build the Gene and Orthologous Gene nodes
        gene = Gene(id=gene_id, in_taxon=gene_ncbitaxon, source="infores:entrez")
        ortholog = Gene(id=ortholog_id, in_taxon=ortholog_ncbitaxon, source="infores:entrez")
        
        # Instantiate the instance of Gene-to-Gene Homology Association
        association = GeneToGeneHomologyAssociation(
            id=f"uuid:{str(uuid.uuid1())}",
            subject=gene.id,
            object=ortholog.id,
            predicate=predicate,
            relation=relation,
            source="infores:panther"
        )
    
        # Write the captured Association out
        koza_app.write(gene, ortholog, association)
