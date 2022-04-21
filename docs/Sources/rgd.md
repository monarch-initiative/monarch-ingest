The Rat Genome Database (RGD) was established in 1999 and is the premier site for genetic, genomic, phenotype, and disease data generated from rat research. In addition, it provides easy access to corresponding human and mouse data for cross-species comparisons.

* [RGD bulk downloads](https://rgd.mcw.edu/wg/data-menu/)

### Gene to Publication

This ingest uses RGD's gene file which contains publication assocations that are denoted in some way in the publication. We have selected to use a consistent high level term for 'publication' (IAO:0000311) as it is heterogeneous mix of publication types being referenced. Even though it is a gene file, and we have fully populated the gene nodes in the alliance gene information ingest, the RGD file has some information that is not in alliance.

Note, there will be a column mismatch warning on this transform because there are two (UNUSED) columns.


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
