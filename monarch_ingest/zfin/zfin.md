## ZFIN

ZFIN is the Zebrafish Model Organism Database. 

* [ZFIN bulk downloads](https://zfin.org/downloads)

### Gene to Phenotype

This ingest uses ZFIN's clean gene phenotype download file, which only contains phenotypes which can safely be associated to a single affected gene. This ingest is distinct from the Alliance phenotype index because ZFIN builds Entity-Quality-Entity phenotype statements that can be built from post-composed terms (E1a+E1b+Q+E2a+E2b), 

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
    * publication



