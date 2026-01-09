# Comparative Toxicogenomics Database (CTD)

CTD is a robust, publicly available database that aims to advance understanding about how environmental exposures affect human health. It provides manually curated information about chemical–gene/protein interactions, chemical–disease and gene–disease relationships. These data are integrated with functional and pathway data to aid in development of hypotheses about the mechanisms underlying environmentally influenced diseases.

* [CTD Bulk Downloads](http://ctdbase.org/downloads/) 

[Chemical to Disease](#chemical_to_disease)

This ingest takes only the chemical to disease rows where a direct evidence label is applied, and creates ChemicalEntity and Disease nodes connected by a ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation. The the chemical ID row is expected to need a 'MESH:' prefix added, the disease id is used as-is. 

Rows are included only if the direct evidence field is 'therapeutic' and the `biolink:affects` predicate is used to avoid making too strong a claim.

__**Biolink Captured**__

* ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation
  * id (random uuid)
  * subject (chemical id)
  * predicate (`biolink:affects`)
  * object (disease id)
  * publication (pubmed ids provided by file)
  * aggregating_knowledge_source (`["infores:monarchinitiative"]`)
  * primary_knowledge_source (`infores:ctd`)

## Citation

Davis AP, Wiegers TC, Johnson RJ, Sciaky D, Wiegers J, Mattingly CJ Comparative Toxicogenomics Database (CTD): update 2023. Nucleic Acids Res. 2022 Sep 28.