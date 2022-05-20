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


Note that we're calling this the disease to phenotype file because we are filtering out all other
association types, which will be brought in via the Mondo ingest and published ontology file
These associations are:

Aspect == 'I'  
Mode of inheritance for a disease, the pattern in which a particular genetic trait
or disorder is passed from one generation to the next.

Aspect == 'C'
Disease to clinical course associations, which includes onset, mortality, and other terms
related to the temporal aspects of disease.

Note that these associations can also include frequency qualifiers, so if we want to ingest
these we'll need to create a new association in the biolink model that has frequency as a slot.

Examples:

```csv
ORPHA:93473	Hurler syndrome		HP:0001522	ORPHA:93473	TAS		HP:0040282			C	ORPHA:orphadata[2021-10-10]
ORPHA:452	X-linked lissencephaly with abnormal genitalia		HP:0001522	ORPHA:452	TAS		HP:0040282			C	ORPHA:orphadata[2021-10-10]
ORPHA:99742	Amish lethal microcephaly		HP:0001522	ORPHA:99742	TAS		HP:0040281			C	ORPHA:orphadata[2021-10-10]
ORPHA:2241	Megacystis-microcolon-intestinal hypoperistalsis syndrome		HP:0001522	ORPHA:2241	TAS		HP:0040283			C	ORPHA:orphadata[2021-10-10]
ORPHA:1790	Hypomandibular faciocranial dysostosis		HP:0001522	ORPHA:1790	TAS		HP:0040283			C	ORPHA:orphadata[2021-10-10]
```

Aspect == 'M'

Disease to clinical modifier associations.

Note that these associations can also include frequency qualifiers, so if we want to ingest
these we'll need to create a new association in the biolink model that has frequency as a slot.

Examples:

```csv
OMIM:236100	Holoprosencephaly 1		HP:0003828	OMIM:236100	TAS					M	HPO:skoehler[2017-07-13]
OMIM:236100	Holoprosencephaly 1		HP:0003829	OMIM:236100	TAS					M	HPO:skoehler[2017-07-13]
OMIM:617087	Charcot-Marie-Tooth disease, axonal, autosomal recessive, type 2A2B		HP:0003828	OMIM:617087	TAS					M	HPO:skoehler[2017-07-13]
ORPHA:101330	Porphyria cutanea tarda		HP:0032500	ORPHA:101330	TAS		HP:0040281			M	ORPHA:orphadata[2021-10-10]
ORPHA:398147	Persistent idiopathic facial pain		HP:0025282	ORPHA:398147	TAS		HP:0040282			M	ORPHA:orphadata[2021-10-10]
ORPHA:447788	Cerebral visual impairment		HP:0025315	ORPHA:447788	TAS		HP:0040283			M	ORPHA:orphadata[2021-10-10]
```

#### Biolink captured

* biolink:Disease
    * id

* biolink:PhenotypicFeature
    * id

* biolink:Publication
    * id
    * type

* biolink:DiseaseToPhenotypicFeatureAssociation
    * id (random uuid)
    * subject (disease.id)
    * predicate (has_phenotype)
    * object (phenotypicFeature.id)
    * relation (RO:0002200)
    * publication (publication.id)
    * evidence 

### Gene to Phenotype (with Disease and HPO Frequency Context)

The gene-to-phenotype ingest processes the tab-delimited [HPOA gene_to_phenotype.txt](http://purl.obolibrary.org/obo/hp/hpoa/gene_to_phenotype.txt) file, which has the following fields:

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
 