# ZFIN

ZFIN is the Zebrafish Model Organism Database. 

* [ZFIN bulk downloads](https://zfin.org/downloads)

## [Gene to Phenotype](#gene_to_phenotype)

This ingest uses ZFIN's clean gene phenotype download file, which only contains phenotypes which can safely be associated to a single affected gene. This ingest is distinct from the Alliance phenotype index because ZFIN builds Entity-Quality-Entity phenotype statements that can be built from post-composed terms (E1a+E1b+Q+E2a+E2b), 

__**Biolink captured**__

* biolink:Gene
    * id

* biolink:PhenotypicFeature
    * id

* biolink:GeneToPhenotypicFeatureAssociation
    * id (random uuid)
    * subject (gene.id)
    * predicate (has_phenotype)
    * object (phenotypicFeature.id)
    * publications
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source (infores:zfin)

## [Gene Literature](#publication_to_gene)

This ingest uses ZFIN's gene to publication download file, which only contains assocations between publications and genes that are denoted in some way in the publication. We have selected to use a consistent high level term for 'publication' (IAO:0000311) as it is heterogeneous mix of publication types being referenced. We have also opted to use the ZDB-ID for the publication node rather than a pubmed ID, on the assumption that kgx will clique merge them later.

__**Biolink captured**__

* biolink:Gene
    * id

* biolink:Publication
    * id

* biolink:InformationContentEntityToNamedThingAssociation
    * id (random uuid)
    * subject (gene.id)
    * predicate (mentions)
    * object (publication.id)
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source (infores:zfin)

## Citation

Bradford, Y.M., Van Slyke, C.E., Ruzicka, L., Singer, A., Eagle, A., Fashena, D., Howe, D.G., Frazer, K., Martin, R., Paddock, H., Pich, C., Ramachandran, S., Westerfield, M. (2022) Zebrafish Information Network, the knowledgebase for Danio rerio research. Genetics. 220(4).