# HGNC (HUGO Gene Nomenclature Committee)

The HGNC is responsible for approving unique symbols and names for human loci, including protein coding genes, ncRNA genes and pseudogenes, to allow unambiguous scientific communication.

* [HGNC bulk downloads](https://www.genenames.org/download/archive/)

## [Gene Information](#gene)

This ingest uses HGNC's "complete set" download file, which only contains associations between publications and genes that are denoted in some way in the publication. We have selected to use a consistent high level term for 'publication' (IAO:0000311) as it is heterogeneous mix of publication types being referenced. 

__**Biolink Captured**__

* biolink:Gene
    * id (HGNC identifier)
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
    * in_taxon (["NCBITaxon:9606"])
    * provided_by  (["infores:hgnc"])

## Citation

HGNC Database, HUGO Gene Nomenclature Committee (HGNC), European Molecular Biology Laboratory, European Bioinformatics Institute (EMBL-EBI), Wellcome Genome Campus, Hinxton, Cambridge CB10 1SD, United Kingdom www.genenames.org. 