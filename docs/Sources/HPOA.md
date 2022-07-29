The [Human Phenotype Ontology](http://human-phenotype-ontology.org) group
curates and assembles over 115,000 annotations to hereditary diseases
using the HPO ontology. Here we create Biolink associations
between diseases and phenotypic features, together with their evidence,
and age of onset and frequency (if known).

There are two HPOA ingests: gene-to-disease and gene-to-phenotype.

The gene-to-disease parser currently only processes the "abnormal" annotations.
Association to "remarkable normality" will be added in the near future.

[HPO Annotation File](http://purl.obolibrary.org/obo/hp/hpoa/phenotype.hpoa)

### Disease to Phenotype

phenotype.hpoa: [A description of this file is found here](https://hpo-annotation-qc.readthedocs.io/en/latest/annotationFormat.html#phenotype-hpoa-format)


Note that we're calling this the disease to phenotype file because - using the YAML file configuration for the ingest -
we are only parsing rows with 'Aspect' types 'I' relating to mode of inheritance, 'C' relating to clinical course and
'M' relating to clinical modifiers, but ignoring the **Aspect == 'P'** rows of data.

#### Biolink captured

* biolink:Disease
    * id
    * has_attribute=["HP term"],  # some child term of "HP:0000005" Mode of Inheritance 
    * provided_by=["infores:hpoa"]
  
* biolink:PhenotypicFeature
    * id

* biolink:Onset
    * id (HP term)

* biolink:Publication
    * id
    * type

* biolink:DiseaseToPhenotypicFeatureAssociation
    * id (random uuid)
    * subject (disease.id)
    * predicate (has_phenotype)
    * negated (True if 'qualifier' == "NOT")
    * object (phenotypicFeature.id)
    * publications (List[publication.id])
    * has_evidence (List[Note [1]]),
    * sex_qualifier (Note [2]) 
    * onset_qualifier (Onset.id)
    * frequency_qualifier (Note [3])
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source ("infores:hpoa")

Notes:
1. CURIE of [Evidence and Conclusion Ontology(https://bioportal.bioontology.org/ontologies/ECO)] term
2. female -> PATO:0000383, male -> PATO:0000384 or None
3. See 8. Frequency in https://hpo-annotation-qc.readthedocs.io/en/latest/annotationFormat.html#phenotype-hpoa-format

### Gene to Phenotype (with Disease and HPO Frequency Context)

The gene-to-phenotype ingest processes the tab-delimited [HPOA gene_to_phenotype.txt](http://purl.obolibrary.org/obo/hp/hpoa/genes_to_phenotype.txt) file, which has the following fields:

  - entrez-gene-id
  - entrez-gene-symbol
  - HPO-Term-ID
  - HPO-Term-Name
  - Frequency-Raw
  - Frequency-HPO
  - Additional Info from G-D source
  - G-D source
  - disease-ID for link

#### Biolink captured

* biolink:Gene
    * id ("NCBIGene:<entrez-gene-id>")

* biolink:PhenotypicFeature
    * id ("<HPO-Term-ID>")

* biolink:Disease
    * id ("<disease-ID for link>")

* biolink:GeneToPhenotypicFeatureAssociation
    * id (random uuid)
    * subject (gene.id)
    * predicate (has_phenotype)
    * object (phenotypicFeature.id)
    * qualifiers (disease.id, (optional - phenotypicFeature.id, where the id is a given "<Frequency-HPO term>"))
    * has_evidence (<G-D source name>)
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source (infores:hpoa)
 