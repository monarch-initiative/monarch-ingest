Online Mendelian Inheritance in Man®. OMIM is a comprehensive, authoritative compendium
of human genes and genetic phenotypes that is freely available and updated daily.
The full-text, referenced overviews in OMIM contain information on all known mendelian
disorders and over 16,000 genes. OMIM focuses on the relationship between phenotype and genotype.

The Monarch Ingest of OMIM involves parsing the morbid map file described here:  
https://www.omim.org/downloads  
https://www.omim.org/help/faq#1_5  

We also use OMIM's mim2gene mapping file when an OMIM identifier represents both
a disease and the genomic loci, for example here:
https://omim.org/entry/104000  

In these cases we get the OMIM to NCBIGene (Entrez) mapping and use the NCBI identifier
for the nucleic acid entity (phenotypic heritable marker) and the OMIM identifier 
for the disease

Currently, we are only pulling in gene disease associations with evidence of a
causal mendelian association between a variation and a disease.  For susceptibility
and other association types we will aim to curate those associations from the OMIM
dataset.

Notes:
In Monarch we call a OMIM phenotypes a "disease", while calling an HPO phenotype a "phenotypic feature".

We directly link the gene and the disease, rather than connecting the variant or genotype 
associated with each disease.  This information can be fetched from the OMIM API or alternatively
from ClinVar.

#### Biolink captured

* biolink:Gene
    * id
    
* "Disorder" (biolink:NucleicAcidEntity or biolink:Disease)
    * id (OMIM ID)

* biolink:GeneToDiseaseAssociation
    * id (random uuid)
    * subject (gene.id)
    * predicate (has_phenotype)
    * object (disorder.id)
    * has_evidence
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source (infores:omim)
