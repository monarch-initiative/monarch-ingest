# Human Phenotype Ontology Annotations (HPOA)

The [Human Phenotype Ontology](http://human-phenotype-ontology.org) group
curates and assembles over 115,000 annotations to hereditary diseases
using the HPO ontology. Here we create Biolink associations
between diseases and phenotypic features, together with their evidence,
and age of onset and frequency (if known).

There are four HPOA ingests - 'disease-to-phenotype', 'disease-to-mode-of-inheritance', 'gene-to-disease' and 'disease-to-mode-of-inheritance' - that parse out records from the [HPO Annotation File](http://purl.obolibrary.org/obo/hp/hpoa/phenotype.hpoa).

The 'disease-to-phenotype', 'disease-to-mode-of-inheritance' and 'gene-to-disease' parsers currently only process the "abnormal" annotations.
Association to "remarkable normality" may be added in the near future.

The 'disease-to-mode-of-inheritance' ingest script parses 'inheritance' record information out from the annotation file.

## [Gene to Disease](#gene_to_disease)

This ingest replaces the direct OMIM ingest so that we share g2d associations 1:1 with HPO. The mapping between association_type and biolink predicates shown below is the one way in which this ingest is opinionated, but attempts to be a direct translation into the biolink model.

**genes_to_disease.txt** with the following fields:

  - 'ncbi_gene_id'
  - 'gene_symbol'
  - 'association_type'
  - 'disease_id'
  - 'source'

__**Biolink Captured**__

* biolink:CorrelatedGeneToDiseaseAssociation or biolink:CausalGeneToDiseaseAssociation (depending on predicate)
    * id (random uuid)
    * subject (ncbi_gene_id)
    * predicate (association_type)
      * MENDELIAN: `biolink:causes`
      * POLYGENIC: `biolink:contributes_to`
      * UNKNOWN: `biolink:gene_associated_with_condition`
    * object (disease_id)
    * primary_knowledge_source (source)
      * medgen: `infores:omim`
      * orphanet: `infores:orphanet`
    * aggregator_knowledge_source (["infores:monarchinitiative"])
      * also for medgen: `infores:medgen`

## [Disease to Phenotype](#disease_to_phenotype)

**phenotype.hpoa:** [A description of this file is found here](https://hpo-annotation-qc.readthedocs.io/en/latest/annotationFormat.html#phenotype-hpoa-format), has the following fields:

  - 'database_id'
  - 'disease_name'
  - 'qualifier'
  - 'hpo_id'
  - 'reference'
  - 'evidence'
  - 'onset'
  - 'frequency'
  - 'sex'
  - 'modifier'
  - 'aspect'
  - 'biocuration'


Note that we're calling this the disease to phenotype file because - using the YAML file filter configuration for the ingest - we are only parsing rows with **Aspect == 'P' (phenotypic anomalies)**, but ignoring all other Aspects.

__**Frequencies**__

The 'Frequency' field of the aforementioned **phenotypes.hpoa** file has the following definition, excerpted from its [Annotation Format](https://hpo-annotation-qc.readthedocs.io/en/latest/annotationFormat.html#phenotype-hpoa-format) page:

    8. Frequency: There are three allowed options for this field. (A) A term-id from the HPO-sub-ontology below the term “Frequency” (HP:0040279). (since December 2016 ; before was a mixture of values). The terms for frequency are in alignment with Orphanet. * (B) A count of patients affected within a cohort. For instance, 7/13 would indicate that 7 of the 13 patients with the specified disease were found to have the phenotypic abnormality referred to by the HPO term in question in the study referred to by the DB_Reference; (C) A percentage value such as 17%.

Previously this ingest attempted to map the quantitative frequency values to HPO frequency terms. The only frequency mapping that occurs is between numerical values now, if a fraction is given it will be split into has_count and has_total, and has_quotient will be calculated by division of has_count/has_total, and has_percentage will be calculated by multiplying has_quotient by 100.

__**Reference**__

The phenotype.hpoa format includes a `DB_reference` field described as:

     5. DB_Reference: This required field indicates the source of the information used for the annotation. This may be the clinical experience of the annotator or may be taken from an article as indicated by a PubMed id. Each collaborating center of the Human Phenotype Ontology consortium is assigned a HPO:Ref id. In addition, if appropriate, a PubMed id for an article describing the clinical abnormality may be used.

This ingest preserves values of DB_reference which are not duplicates of the database_id captured as the subject, and will ultimately be found in `original_subject` in the graph when the subject is mapped via SSSOM to a Mondo identifier.

__**Biolink captured**__

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
    * primary_knowledge_source ("infores:hpo-annotations")

Notes:
1. CURIE of [Evidence and Conclusion Ontology(https://bioportal.bioontology.org/ontologies/ECO)] term
2. female -> PATO:0000383, male -> PATO:0000384 or None
3. See the [Frequencies](#frequencies) section above.

## [Disease to Modes of Inheritance](#disease_modes_of_inheritance)

Same as above, we again parse the [phenotype.hpoa file](https://hpo-annotation-qc.readthedocs.io/en/latest/annotationFormat.html#phenotype-hpoa-format).

However, we're calling this the 'disease to modes of inheritance' file because - using the YAML file filter configuration for the ingest - we are only parsing rows with **Aspect == 'I' (inheritance)**, but ignoring all other Aspects.

__**Biolink captured**__

* biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation
    * id (random uuid)
    * subject (disease.id)
    * predicate (has_mode_of_inheritance)
    * object (geneticInheritance.id)
    * publications (List[publication.id])
    * has_evidence (List[Note [1]]),
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source ("infores:hpo-annotations")

## [Gene to Phenotype](#gene_to_phenotype)

The gene-to-phenotype ingest processes the tab-delimited [HPOA gene_to_phenotype.txt](http://purl.obolibrary.org/obo/hp/hpoa/genes_to_phenotype.txt) file, which has the following fields:

  - 'ncbi_gene_id'
  - 'gene_symbol'
  - 'hpo_id'
  - 'hpo_name'

__**Biolink captured**__

* biolink:GeneToPhenotypicFeatureAssociation
    * id (random uuid)
    * subject (gene.id)
    * predicate (has_phenotype)
    * object (phenotypicFeature.id)
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source (infores:hpo-annotations)
 
## Citation

Sebastian Köhler, Michael Gargano, Nicolas Matentzoglu, Leigh C Carmody, David Lewis-Smith, Nicole A Vasilevsky, Daniel Danis, Ganna Balagura, Gareth Baynam, Amy M Brower, Tiffany J Callahan, Christopher G Chute, Johanna L Est, Peter D Galer, Shiva Ganesan, Matthias Griese, Matthias Haimel, Julia Pazmandi, Marc Hanauer, Nomi L Harris, Michael J Hartnett, Maximilian Hastreiter, Fabian Hauck, Yongqun He, Tim Jeske, Hugh Kearney, Gerhard Kindle, Christoph Klein, Katrin Knoflach, Roland Krause, David Lagorce, Julie A McMurry, Jillian A Miller, Monica C Munoz-Torres, Rebecca L Peters, Christina K Rapp, Ana M Rath, Shahmir A Rind, Avi Z Rosenberg, Michael M Segal, Markus G Seidel, Damian Smedley, Tomer Talmy, Yarlalu Thomas, Samuel A Wiafe, Julie Xian, Zafer Yüksel, Ingo Helbig, Christopher J Mungall, Melissa A Haendel, Peter N Robinson, The Human Phenotype Ontology in 2021, Nucleic Acids Research, Volume 49, Issue D1, 8 January 2021, Pages D1207–D1217, https://doi.org/10.1093/nar/gkaa1043