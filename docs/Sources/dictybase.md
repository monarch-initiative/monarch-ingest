# Dictybase

Dictybase is a comprehensive database for the ameboid protozoan _Dictyostelium discoideum_, which is a powerful model system for genetic and functional analysis of gene function.

* [Dictybase Bulk Downloads](http://dictybase.org/db/cgi-bin/dictyBase/download)


## [Gene Information](#gene)

Dictybase genes in the Gene to Phenotype ingest (below) are either directly identified from their gene identifier, mapped directly to [NCBI _Dictyostelium discoideum_ gene identifier mappings](https://www.ncbi.nlm.nih.gov/data-hub/gene/table/taxon/352472/) or mapped indirectly from the [Dictybase identifier, names and synonyms mappings](http://dictybase.org/Downloads/gene_information.html), with synonyms being populated as available (Note: full gene product information is not captured at this time).

## [Gene to Phenotype](#gene_to_phenotype)

Data is available in a well-documented easy-to-parse GAF-like format with associations to an UPHENO-compliant ontology. Phenotypes are linked to Strains, and the Strains are linked to Genes.

__**Biolink Captured**__

* biolink:Gene
    * 'id' (NCBI or Dictybase)
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


## Citation

Fey, P., Dodson, R., Basu, S., Chisholm, R. L. (2013). 'One Stop Shop for Everything Dictyostelium: dictyBase and the Dicty Stock Center'. Dictyostelium discoideum Protocols. Methods Mol. Biol. 983:59-92, edited by Ludwig Eichinger and Francisco Rivero.
