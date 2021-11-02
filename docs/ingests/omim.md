Online Mendelian Inheritance in Man®. OMIM is a comprehensive, authoritative compendium
of human genes and genetic phenotypes that is freely available and updated daily.
The full-text, referenced overviews in OMIM contain information on all known mendelian
disorders and over 16,000 genes. OMIM focuses on the relationship between phenotype and genotype.

Notes:
In Monarch we call a OMIM phenotypes a "disease", while calling an HPO phenotype a "phenotypic feature".

We directly link the gene and the disease, rather than connecting the variant or genotype 
associated with each disease.  This information can be fetched from the OMIM API or alternatively
from ClinVar.

#### Biolink captured

* biolink:Gene
    * id

* biolink:Disease
    * id

* biolink:GeneToDiseaseAssociation
    * id (random uuid)
    * subject (gene.id)
    * predicate (has_phenotype)
    * object (disease.id)
    * relation (RO:0002200)
    * publication (publication.id)
    * evidence
