# Rat Genome Database (RGD)

The Rat Genome Database (RGD) was established in 1999 and is the premier site for genetic, genomic, phenotype, and disease data generated from rat research. In addition, it provides easy access to corresponding human and mouse data for cross-species comparisons.

* [RGD bulk downloads](https://rgd.mcw.edu/wg/data-menu/)

## [Gene Literature](#publication_to_gene)

This ingest uses RGD's gene file which contains publication assocations that are denoted in some way in the publication. We have selected to use a consistent high level term for 'publication' (IAO:0000311) as it is heterogeneous mix of publication types being referenced. Even though it is a gene file, and we have fully populated the gene nodes in the alliance gene information ingest, the RGD file has some information that is not in alliance.

Note, there will be a column mismatch warning on this transform because there are two (UNUSED) columns.

__**Biolink captured**__

* biolink:Gene
    * id

* biolink:Publication
    * id

* biolink:InformationContentEntityToNamedThingAssociation
    * id (random uuid)
    * subject (gene.id)
    * predicate (mentions)
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source (infores:rgd)

## Citation

Vedi M, Smith JR, Thomas Hayman G, Tutaj M, Brodie KC, De Pons JL, Demos WM, Gibson AC, Kaldunski ML, Lamers L, Laulederkind SJF, Thota J, Thorat K, Tutaj MA, Wang SJ, Zacher S, Dwinell MR, Kwitek AE. 2022 updates to the Rat Genome Database: a Findable, Accessible, Interoperable, and Reusable (FAIR) resource. Genetics. 2023 May 4;224(1):iyad042. doi: 10.1093/genetics/iyad042. PMID: 36930729; PMCID: PMC10474928.