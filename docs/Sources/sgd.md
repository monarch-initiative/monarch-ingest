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

## Citation

Cherry JM, Hong EL, Amundsen C, Balakrishnan R, Binkley G, Chan ET, Christie KR, Costanzo MC, Dwight SS, Engel SR, Fisk DG, Hirschman JE, Hitz BC, Karra K, Krieger CJ, Miyasato SR, Nash RS, Park J, Skrzypek MS, Simison M, Weng S, Wong ED (2012) Saccharomyces Genome Database: the genomics resource of budding yeast. Nucleic Acids Res. Jan;40(Database issue):D700-5. [PMID: 22110037]