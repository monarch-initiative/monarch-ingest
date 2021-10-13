Xenbase is a web-accessible resource that integrates all the diverse biological, genomic, genotype and phenotype data available from Xenopus research.

[Xenbase Bulk Data](http://www.xenbase.org/other/static-xenbase/ftpDatafiles.jsp)
[Xenbase FTP](http://ftp.xenbase.org/pub/)

### Gene Information

Xenbase genes are ingested using Koza's built in support for the GPI format rather than using the gene information file available from the bulk download. The GPI file is downloaded from [http://ftp.xenbase.org/pub/GenePageReports/xenbase.gpi.gz](http://ftp.xenbase.org/pub/GenePageReports/xenbase.gpi.gz)

#### Biolink captured

* Gene
  * id
  * symbol
  * name
  * synonym
  * in_taxon
  * xref
  * source

### Gene to Phenotype

This ingest is built against a one-off OBAN formatted file, which makes for a transformation which only requries adding a curie prefix and connecting column names to biolink attributes. Evidence codes are provided as ECO terms but not yet captured in the output. 

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
    
### Gene Literature

This ingest reads from Xenbase's [Genes Associated with Literature](http://ftp.xenbase.org/pub/GenePageReports/LiteratureMatchedGenesByPaper.txt) file to capture associations between Xenbase's XB-GENEPAGE ids and PMIDs, then relies on a map built from Xenbase's [GenepageToGeneId](http://ftp.xenbase.org/pub/GenePageReports/XenbaseGenepageToGeneIdMapping.txt) file to create associations from XB-GENE records to PMID records.

#### Biolink captured

* Gene
    * id

* Publication
    * id
    
* NamedThingToInformationContentEntityAssociation
    * id (random uuid)
    * subject (gene.id)
    * predicate (mentions)
    * object (publication.id)
    * relation (mentions)
    
