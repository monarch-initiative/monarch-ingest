## STRING: functional protein association networks

[STRING is a database of known and predicted protein-protein interactions](https://string-db.org/cgi/about). The interactions include direct (physical) and indirect (functional) associations; they stem from computational prediction, from knowledge transfer between organisms, and from interactions aggregated from other (primary) databases.

* [STRING bulk downloads](https://stringdb-static.org/download)

### Protein Links (Source File)

This ingest uses a given version (currently, **11.5**) of the STRING's <taxon>.protein.links.detailed.<version>.txt.gz files, for a subset of NCBI <taxon> ID designated species. We filter the input data on the **combined_score** field (currently with the threshhold recorded in the **protein_links.yaml** file). The various [taxon specific entrez_2_string mapping files](https://string-db.org/mapping_files/entrez) are used to map protein subject and concept nodes onto Entrez gene id's.

#### Special note about Entrez mapping files

A separate Entrez to String identifier mapping file is not available for _Rattus norvegicus_ (Norway rat, NCBI taxon ID 10116) but the mappings are (less conveniently) available inside the aggregated ['all_organisms' entrez_2_string file](https://string-db.org/mapping_files/entrez/all_organisms.entrez_2_string.2018.tsv.gz). See notes in the STRING section of the _download.yaml_ configuration file for (self explanatory) guidance on how to prepare the required mapping file for use in a local running of the digest.


### Source File

  * protein1
  * protein2
  * neighborhood
  * fusion
  * cooccurence
  * coexpression
  * experimental
  * database
  * textmining
  * combined_score

### Biolink classes and properties captured

#### Concept Nodes

* **biolink:Gene**
  * id (NCBIGene Entrez ID)

#### Associations

* **biolink:PairwiseGeneToGeneInteraction**:
    * id (random uuid)
    * subject (gene.id)
    * predicate (interacts_with)
    * object (gene.id)
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source (infores:string)
