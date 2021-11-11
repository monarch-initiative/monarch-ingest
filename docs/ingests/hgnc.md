The HGNC is responsible for approving unique symbols and names for human loci, including protein coding genes, ncRNA genes and pseudogenes, to allow unambiguous scientific communication.

* [HGNC bulk downloads](https://www.genenames.org/download/archive/)

### Gene Information

This ingest uses ZFIN's gene to publication download file, which only contains assocations between publications and genes that are denoted in some way in the publication. We have selected to use a consistent high level term for 'publication' (IAO:0000311) as it is heterogeneous mix of publication types being referenced. 

#### Biolink captured

* biolink:Gene
    * id
    * symbol
    * name
    * synonym
      * alias symbol
      * alias name
      * prev symbol
      * prev name
    * xref
      * ensembl gene id
      * omim id

* biolink:Publication
    * id

* biolink:NamedThingToInformationContentEntityAssociation
    * id (random uuid)
    * subject (gene.id)
    * predicate (mentions)
    * object (publication.id)
    * relation (mentions)
