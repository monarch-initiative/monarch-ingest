Dictybase is a comprehensive database for the ameboid protozoan _Dictyostelium discoideum_, which is a powerful model system for genetic and functional analysis of gene function.

* [Dictybase Bulk Downloads](http://dictybase.org/db/cgi-bin/dictyBase/download)


### Gene Information

Dictybase genes in the Gene to Phenotype ingest (below) are either directly identified from their gene identifier, or mapped indirectly from the [Dictybase identifier, names and synonyms mappings](http://dictybase.org/Downloads/gene_information.html), with synonyms being populated as available (Note: full gene product information is not captured at this time).

### Gene to Phenotype

Data is available in a well-documented easy-to-parse GAF-like format with associations to an UPHENO-compliant ontology. Phenotypes are linked to Strains, and the Strains are linked to Genes.

#### Biolink captured

* biolink:Gene
    * 'id'
    * 'category'
    * 'name'
    * 'symbol'
    * 'in_taxon'
    * 'source'

* biolink:PhenotypicFeature
    * id

* biolink:GeneToPhenotypicFeatureAssociation
    * id (random uuid)
    * subject (gene.id)
    * predicate (has_phenotype)
    * object (phenotypicFeature.id)
    * category (GeneToPhenotypicFeatureAssociation)
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source (infores:dictybase)

