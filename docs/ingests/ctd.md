CTD is a robust, publicly available database that aims to advance understanding about how environmental exposures affect human health. It provides manually curated information about chemical–gene/protein interactions, chemical–disease and gene–disease relationships. These data are integrated with functional and pathway data to aid in development of hypotheses about the mechanisms underlying environmentally influenced diseases.

* [CTD Bulk Downloads](http://ctdbase.org/downloads/) 

### Chemical to Disease

This ingest takes only the chemical to disease rows where a direct evidence label is applied, and creates ChemicalEntity and Disease nodes connected by a ChemicalToDiseaseOrPhenotypicFeatureAssociation. The the chemical ID row is expected to need a 'MESH:' prefix added, the disease id is used as-is. 

If the direct evidence field is 'marker/mechanism' the `biolink:biomarker_for` predicate is used along with the "is marker for" relation from RO.
If the direct evidence field is 'therapeutic' the `biolink:treats` predicate is used along with the "is substance that treats" relation from RO.

#### Biolink captured

* ChemicalEntity
  * id (MeSH id)
  * name

* Disease
  * id (MeSH or OMIM)
  * name

* ChemicalToDiseaseOrPhenotypicFeatureAssociation
  * id (random uuid)
  * subject (chemical id)
  * predicate (mapping from DirectEvidence column)
  * object (disease id)
  * publication (pubmed ids provided by file)
  * relation 

