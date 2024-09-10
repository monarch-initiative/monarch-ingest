# Alliance 

The Alliance of Genome Resources contains a subset of model organism data from member databases that is harmonized to the same model. Over time, as the alliance adds additional data types, individual MOD ingests can be replaced by collective Alliance ingest. The Alliance has bulk data downloads, ingest data formats, and an API. The preference should be bulk downloads first, followed by ingest formats, finally by API calls. In some cases it may continue to be more practical to load from individual MODs when data is not yet fully harmonized in the Alliance.

* [Alliance Bulk Downloads](https://www.alliancegenome.org/downloads)
* [Alliance schemas](https://github.com/alliance-genome/agr_schemas)

## [Gene Information](#gene)

Genes for all Alliance species (Human, Rat, Mouse, Fish, Fly, Worm, Yeast, Frog) are loaded using the [BGI formatted](https://github.com/alliance-genome/agr_schemas/tree/master/ingest/gene) ingest files, as there are no Gene export files.

__**Biolink captured**__

* biolink:Gene
    * id
    * symbol
    * name
    * in_taxon
    * source
    * synonyms
    * xref
    * type (["SO:0001217"])


## [Gene to Phenotype](#gene_to_phenotype)

Phenotype for the subset of Alliance species which use phenotype ontologies (Human, Rat, Mouse, Worm) are loaded using the [phenotype ingest format](https://github.com/alliance-genome/agr_schemas/tree/master/ingest/phenotype), since there is not yet a phenotype export file from the Alliance. This file contains both Gene and Allele phenotypes, so a single column TSV is produced from BGI files listing Gene IDs to check the category and only genes are included. Environmental conditions are present for some species and are captured using the qualifier.

__**Biolink captured**__

* biolink:GeneToPhenotypicFeatureAssociation
    * id (random uuid)
    * subject (gene.id)
    * predicate (has_phenotype)
    * object (phenotypicFeature.id)
    * publications
    * qualifiers (condition terms)
    * aggregating_knowledge_source (["infores:monarchinitiative", "infores:alliancegenome"])
    * primary_knowledge_source (`infores` mapped from row['Source'])

## [Gene Expression](#gene_to_expression)

This is the full data model of the Alliance file ingested; however, not all fields are currently used in the current ingest (in most cases, these fields are not yet set in the input data sets; see the gene_to_expression.yaml file)

* Species
* SpeciesID
* GeneID
* GeneSymbol
* Location
* StageTerm
* AssayID
* AssayTermName
* CellularComponentID
* CellularComponentTerm
* CellularComponentQualifierIDs
* CellularComponentQualifierTermNames
* SubStructureID
* SubStructureName
* SubStructureQualifierIDs
* SubStructureQualifierTermNames
* AnatomyTermID
* AnatomyTermName
* AnatomyTermQualifierIDs
* AnatomyTermQualifierTermNames
* SourceURL
* Source
* Reference

**Discussion Group**: https://www.alliancegenome.org/working-groups#expression  

**Download**: https://www.alliancegenome.org/downloads#expression

__**Biolink captured**__

* biolink:Gene
    * id (row['GeneID'])
    * name (row['GeneSymbol'])
    * in taxon (row['SpeciesID'])
    * source (`infores` mapped from row['Source'])

* biolink:AnatomicalEntity
    * id (row['AnatomyTermID'])
    * name (row['AnatomyTermName'])
    * source (`infores` mapped from row['Source'])

* biolink:CellularComponent  # is_a: anatomical entity...
    * id (row['CellularComponentID'])
    * name (row['CellularComponentTerm'])
    * source (`infores` mapped from row['Source'])

* biolink:LifeStage
    * id (CURIE heuristically inferred from row['SpeciesID'] and row['StageTerm'])
    * name (row['StageTerm'])
    * in taxon (row['SpeciesID'])
    * source (`infores` mapped from row['Source'])

* biolink:GeneToExpressionSiteAssociation
    * id (random uuid)
    * subject (Gene.id)
    * predicates (biolink:expressed_in)
    * object (AnatomicalEntity.id or CellularComponent.id)
    * stage qualifier (LifeStage.id)  # if specified; None otherwise
    * has evidence (row['AssayID'])  # e.g. taken from MMO - "measurement method ontology"
    * publications (row['Reference'])
    * aggregating_knowledge_source (["infores:monarchinitiative", "infores:alliancegenome"])
    * primary_knowledge_source (`infores` mapped from row['Source'])

## [Literature](#publication)

The Alliance has a [well defined](https://github.com/alliance-genome/agr_schemas/tree/master/ingest/resourcesAndReferences) literature ingest format that aligns publications from MOD members. 

Mapping of Alliance publication category to biolink category

| Alliance category          | Biolink publication type |
|----------------------------|--------------------------|
| Research Article           | IAO:0000013              |
| Review Article             | IAO:0000013              |
| Thesis                     | IAO:0000311              |
| Book                       | IAO:0000311              |
| Other                      | IAO:0000311              |
| Preprint                   | IAO:0000013              |
| Conference Publication     | IAO:0000311              |
| Personal Communication     | IAO:0000311              |
| Direct Data Submission     | IAO:0000311              |
| Internal Process Reference | IAO:0000311              |
| Unknown                    | IAO:0000311              |
| Retraction                 | IAO:0000311              |

This ingest doesn't make an effort to sort these publication categories into more specific classes than biolink:Publication, but does set the type.

__**Biolink captured**__

* biolink:Publication
    * id (primaryId) 
    * name (title)
    * summary (abstract)
    * authors (authors.name flattened as a comma separated string)
    * xref (crossReferences.id)
    * mesh terms (meshTerms.meshHeadingTerm , meshTerms.meshQualifierTerm)
    * type (IAO:0000311 for publication, IAO:0000013 for article)
    * creation date (datePublished)
    * keywords (keywords)

## Citation

Harmonizing model organism data in the Alliance of Genome Resources. 2022. Alliance of Genome Resources Consortium. Genetics, Volume 220, Issue 4, April 2022. Published Online: 25 February 2022. doi: doi.org/10.1093/genetics/iyac022. PMID: 35380658;  PMCID: PMC8982023.