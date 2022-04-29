FlyBase is the model organism database providing integrated genetic, genomic, phenomic, and biological data for Drosophila melanogaster.

* [FlyBase bulk downloads](http://flybase.org/downloads/bulkdata)

### Gene to Publication

This ingest uses FlyBase's gene to publication download file, which contains all entities and only assocations between publications and genes that are denoted in some way in the publication. We have selected to use a consistent high level term for 'publication' (IAO:0000311) as it is heterogeneous mix of publication types being referenced. We have also opted to use the FlyBase_publication_id for the publication node if PubMed_id is not available, on the assumption that kgx will clique merge them later.

#### Biolink captured

* biolink:Gene
    * id

* biolink:Publication
    * id

* biolink:InformationContentEntityToNamedThingAssociation
    * id (random uuid)
    * subject (gene.id)
    * predicate (mentions)
    * object (publication.id)
    * relation (mentions)
