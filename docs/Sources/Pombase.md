PomBase is a comprehensive database for the fission yeast Schizosaccharomyces pombe, providing structural and functional annotation, literature curation and access to large-scale data sets. Within this ingest there will be a transformation of gene to phenotypic feature associations, gene entities aren't yet loaded as a part of this ingest, and FYPO ontology terms will be brought in directly from the ontology without transformation.

* [PomBase Bulk Downloads](https://www.pombase.org/datasets)
* [Phaf Format Description](https://www.pombase.org/downloads/phenotype-annotations)
* [Phaf Format LinkML](https://biodatamodels.github.io/ontology-associations/PombasePhafAssociation/)

### Gene Information

PomBase genes are captured directly from the PomBase (names and identifiers)[https://www.pombase.org/downloads/names-and-identifiers] set, with synonyms being populated as available and UniProtKB accessions captured as xrefs if available.   

#### Biolink Captured

* biolink:Gene
  * id
  * symbol
  * type (SO term ids mapped through the global translation table)
  * xref (UniProfKB curie if provided)
  * synonyms
  * source

### Gene to Phenotype

The [PHAF](https://www.pombase.org/downloads/phenotype-annotations) download file is extremely well documented. Alleles provided, but not captured, with the assumption that even with an allele specified the gene to phenotype is accurate with a some-some interpretation. Genotype/strain information looks uniform throughout the file, and is not captured. It might be sensible to make presence of genotype information an error condition to be sure that we only get 'clean' gene to phenotype associations.  

Penetrance and Severity columns are available, but not captured as a part of this ingest. Penetrance values can be either FYPO_EXT terms (FYPO_EXT:0000001, FYPO_EXT:0000002, FYPO_EXT:0000003, FYPO_EXT:0000004), int/float numbers (percentages), or strings (">98", "~10", "10-20"). Severity is represented using one or more FYPO_EXT terms.

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
    * publications
    * qualifers (optionally included from condition row)
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source (infores:pombase)
