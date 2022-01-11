## STRING: functional protein association networks

[STRING is a database of known and predicted protein-protein interactions](https://string-db.org/cgi/about). The interactions include direct (physical) and indirect (functional) associations; they stem from computational prediction, from knowledge transfer between organisms, and from interactions aggregated from other (primary) databases.

* [STRING bulk downloads](https://stringdb-static.org/download)

### Protein Links (Source File)

This ingest uses a given version (currently, **11.5**) of the STRING's <taxon>.protein.links.detailed.<version>.txt.gz files, for a subset of NCBI <taxon> ID designated species. We filter the input data on the **combined_score** field (currently with the threshhold recorded in the **protein_links.yaml** file)

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

* **biolink:Protein**
  * id
  * in taxon (NCBITaxon ID)
  * source (ENSEMBL)

#### Associations

* **biolink:PairwiseGeneToGeneInteraction**:
    * id (random uuid)
    * subject (protein.id)
    * predicate (interacts_with)
    * object (protein.id)
    * relation (RO:0002434)
    * provided_by (infores:string)
