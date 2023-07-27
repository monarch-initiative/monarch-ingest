# Saccharomyces Genome Database (SGD)

The Saccharomyces Genome Database (SGD) provides comprehensive integrated biological information for the budding yeast Saccharomyces cerevisiae along with search and analysis tools to explore these data, enabling the discovery of functional relationships between sequence and gene products in fungi and higher organisms.

* [SGD bulk downloads](http://sgd-archive.yeastgenome.org/)

## [Gene Literature](#publication_to_gene)

This ingest uses RGD's gene to publication download file, which only contains assocations between publications and genes that are denoted in some way in the publication. We have selected to use a consistent high level term for 'publication' (IAO:0000311) as it is heterogeneous mix of publication types being referenced. 

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
    * primary_knowledge_source (infores:sgd)
