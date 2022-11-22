The [Human Phenotype Ontology](http://human-phenotype-ontology.org) group
curates and assembles over 115,000 annotations to hereditary diseases
using the HPO ontology. Here we create Biolink associations
between diseases and phenotypic features, together with their evidence,
and age of onset and frequency (if known).

There are four HPOA ingests - 'disease-to-phenotype', 'disease-to-mode-of-inheritance', 'gene-to-disease' and 'disease-to-mode-of-inheritance' - that parse out records from the [HPO Annotation File](http://purl.obolibrary.org/obo/hp/hpoa/phenotype.hpoa).

The 'disease-to-phenotype', 'disease-to-mode-of-inheritance' and 'gene-to-disease' parsers currently only process the "abnormal" annotations.
Association to "remarkable normality" may be added in the near future.

The 'disease-to-mode-of-inheritance' ingest script parses 'inheritance' record information out from the annotation file.

### Disease to Phenotype

**phenotype.hpoa:** [A description of this file is found here](https://hpo-annotation-qc.readthedocs.io/en/latest/annotationFormat.html#phenotype-hpoa-format), has the following fields:

  - 'DatabaseID'
  - 'DiseaseName'
  - 'Qualifier'
  - 'HPO_ID'
  - 'Reference'
  - 'Evidence'
  - 'Onset'
  - 'Frequency'
  - 'Sex'
  - 'Modifier'
  - 'Aspect'
  - 'Biocuration'

Note that we're calling this the disease to phenotype file because - using the YAML file filter configuration for the ingest - we are only parsing rows with **Aspect == 'P' (phenotypic anomalies)**, but ignoring all other Aspects.

#### Frequencies

The 'Frequency' field of the aforementioned **phenotypes.hpoa** file has the following definition, excerpted from its [Annotation Format](https://hpo-annotation-qc.readthedocs.io/en/latest/annotationFormat.html#phenotype-hpoa-format) page:

    8. Frequency: There are three allowed options for this field. (A) A term-id from the HPO-sub-ontology below the term “Frequency” (HP:0040279). (since December 2016 ; before was a mixture of values). The terms for frequency are in alignment with Orphanet. * (B) A count of patients affected within a cohort. For instance, 7/13 would indicate that 7 of the 13 patients with the specified disease were found to have the phenotypic abnormality referred to by the HPO term in question in the study referred to by the DB_Reference; (C) A percentage value such as 17%.

The Disease to Phenotype ingest attempts to remap these raw frequency values onto a suitable HPO term.  A simplistic (perhaps erroneous?) assumption is that all such frequencies are conceptually comparable; however, researchers may wish to review the original publications to confirm fitness of purpose of the specific data points to their interpretation - specific values could designate phenotypic frequency at the population level; phenotypic frequency at the cohort level; or simply, be a measure of penetrance of a specific allele within carriers, etc..

#### Biolink captured

* biolink:Disease
    * id ((OMIM|DECIPHER|ORPHA) id)
  
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
3. See the [Frequencies](#frequencies) section above.

### Disease to Modes of Inheritance

Same as above, we again parse the [phenotype.hpoa file](https://hpo-annotation-qc.readthedocs.io/en/latest/annotationFormat.html#phenotype-hpoa-format).

However, we're calling this the 'disease to modes of inheritance' file because - using the YAML file filter configuration for the ingest - we are only parsing rows with **Aspect == 'I' (inheritance)**, but ignoring all other Aspects.

#### Biolink captured

* biolink:Disease
    * id ((OMIM|DECIPHER|ORPHA) id)

* biolink:GeneticInheritance
    * id (HP term)

* biolink:Publication
    * id

* biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation
    * id (random uuid)
    * subject (disease.id)
    * predicate (has_mode_of_inheritance)
    * object (geneticInheritance.id)
    * publications (List[publication.id])
    * has_evidence (List[Note [1]]),
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source ("infores:hpoa")

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
 