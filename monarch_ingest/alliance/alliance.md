## Alliance of Genome Resources

The Alliance of Genome Resources contains a subset of model organism data from member databases that is harmonized to the same model. Over time, as the alliance adds additional data types, individual MOD ingests can be replaced by collective Alliance ingest. The Alliance has bulk data downloads, ingest data formats, and an API. The preference should be bulk downloads first, followed by ingest formats, finally by API calls. In some cases it may continue to be more practical to load from individual MODs when data is not yet fully harmonized in the Alliance.

* [Alliance Bulk Downloads](https://www.alliancegenome.org/downloads)
* [Alliance schemas](https://github.com/alliance-genome/agr_schemas)

### Gene Information

Genes for all Alliance species (Human, Rat, Mouse, Fish, Fly, Worm, Yeast) are loaded using the [BGI formatted](https://github.com/alliance-genome/agr_schemas/tree/master/ingest/gene) ingest files, as there are no Gene export files.

#### Biolink captured

* biolink:Gene
    * id
    * symbol
    * name
    * type (Sequence Ontology term ID)
    * in_taxon
    * source
    * synonyms
    * xrefs

### Gene Phenotype

Phenotype for the subset of Alliance species which use phenotype ontologies (Human, Rat, Mouse, Worm) are loaded using the [phenotype ingest format](https://github.com/alliance-genome/agr_schemas/tree/master/ingest/phenotype), since there is not yet a phenotype export file from the Alliance. This file contains both Gene and Allele phenotypes, so a single column TSV is produced from BGI files listing Gene IDs to check the category and only genes are included. Environmental conditions are present for some species and are captured using the qualifier.

#### Biolink captured

* biolink:Gene
    * id

* biolink:PhenotypicFeature
    * id

* biolink:GeneToPhenotypicFeatureAssociation
    * id (random uuid)
    * subject (gene.id)
    * predicate (has_phenotype)
    * object (phenotypicFeature.id)
    * relation (has phenotype)
    * publications
    * qualifiers (condition terms)

