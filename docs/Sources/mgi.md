# Mouse Genome Informatics (MGI)

Mouse Genome Informatics (MGI) is the international database resource for the laboratory mouse, providing integrated genetic, genomic, and biological data to facilitate the study of human health and disease.

* [MGI bulk downloads](http://www.informatics.jax.org/downloads/reports/index.html)

## [Gene Literature](#publication_to_gene)

This ingest uses MGI's Reference download file, which contains genes and a tab-delimited list of PubMed IDs in which they are mentioned. 

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
    * primary_knowledge_source (infores:mgi)
