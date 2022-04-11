The European Bioinformatics Institute Gene2Phenotype (G2P) resource is a publicly-accessible online system designed to facilitate the development, validation, curation and distribution of large-scale, evidence-based datasets for use in diagnostic variant filtering. Each G2P entry associates an allelic requirement and a mutational consequence at a defined locus with a disease entity. A confidence level and evidence link are assigned to each entry.

* [EBI G2P Bulk Downloads](https://www.ebi.ac.uk/gene2phenotype/downloads): the EBI G2P resource currently provides human data partitioned into four broad categories:

  - Cancer gene-disease pairs and attributes (CancerG2P.csv.gz)
  - DD gene-disease pairs and attributes (DDG2P.csv.gz)
  - Eye gene-disease pairs and attributes (EyeG2P.csv.gz)
  - Skin gene-disease pairs and attributes (SkinG2P.csv.gz)

* [EBI G2P Core Data Model](https://www.ebi.ac.uk/gene2phenotype/README)

### Gene Information

Genes for the EBI G2P are essentially human loci assigned with HGNC identifier numbers. Hence, in this ingest, we do not input nor export extensive gene information but rather set the G2P association subject gene id's to their HGNC identifier.

### Gene to Phenotype

The core phenotype data fields  provided in the input data files are:

  - **gene symbol:**  HGNC gene symbol 
  - **gene mim:** OMIM number for a gene entry
  - **disease name:** Name provided by the curator
  - **disease mim:** OMIM number for a disease entry
  - **confidence value:** one value from [the list of possible categories](https://www.ebi.ac.uk/gene2phenotype/updates_to_our_terms#confidence_value) (Note: this field may still be called "confidence category" in legacy data files):
      - both RD and IF
      - definitive
      - strong
      - moderate
      - limited
  - **allelic requirement:**  One value from [the list of possible allelic requirement attributes](https://www.ebi.ac.uk/gene2phenotype/updates_to_our_terms#allelic_requirement). Possible values are:
      - biallelic_autosomal
      - monoallelic_autosomal
      - monoallelic_PAR
      - biallelic_PAR
      - mitochondrial
      - monoallelix_X_hem
      - monallelic_X_het
      - monoallelic_Y_hem   
  - **mutation consequence:** One value from the [list of possible consequences](https://www.ebi.ac.uk/gene2phenotype/updates_to_our_terms#mutation_consequence):
      - 5_prime or 3_prime UTR mutation
      - cis-regulatory or promotor mutation
      - absent gene product
      - altered gene product structure
      - increased gene product level
      - uncertain.
  - **phenotypes:** semicolon-separated list of HPO (http://www.human-phenotype-ontology.org/) IDs
  - **organ specificity list:** semicolon-separated list of organs
  - **pmids:** semicolon-separated list of PMIDs 
  - **panel:** G2P panel:
      - Cancer
      - Cardiac
      - DD
      - Ear
      - Eye
      - Skin
  - **prev symbols:** Symbols previously approved by the HGNC for this gene
  - **hgnc id:** HGNC identifier
  - **gene disease pair entry date:** Entry date for the gene disease pair into the database
  - **cross cutting modifier:** semi-colon separated [list of possible cross-cutting modifier attributes](https://www.ebi.ac.uk/gene2phenotype/updates_to_our_terms#confidence_value):
      - requires heterozygosity
      - typically de novo
      - typically mosaic
      - imprinted
      - typified by age related penetrance
      - typified by reduced penetrance
  - **mutation consequences flag:** One value from [the list of possible flags](https://www.ebi.ac.uk/gene2phenotype/updates_to_our_terms#mutation_consequence):
      - likely to escape nonsense mediated decay
      - part of contiguous gene duplication
      - part of contiguous genomic interval deletion
      - restricted repertoire of mutations
  - **confidence value flag:** if not empty, then [should be set to the value 'requires clinical review'](https://www.ebi.ac.uk/gene2phenotype/updates_to_our_terms#new_confidence_value_flag)
  - **comments:** any additional information about the gene to phenotype relationship that are not captured elsewhere

#### Biolink captured

* biolink:Gene
    * id 

* biolink:PhenotypicFeature
    * id

* biolink:GeneToPhenotypicFeatureAssociation
    * id (random uuid)
    * subject (hgnc id)
    * predicate (has_phenotype)
    * object (phenotypicFeature.id)
    * relation (has phenotype)
    * publications (PMID's)
    * qualifiers (condition terms)
