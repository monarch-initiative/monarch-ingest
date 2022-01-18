## Gene Ontology Annotation Database

The Gene Ontology Annotation Database compiles high-quality [Gene Ontology (GO)](http://www.geneontology.org/) annotations to proteins in the [UniProt Knowledgebase (UniProtKB)](https://www.uniprot.org/), RNA molecules from [RNACentral](http://rnacentral.org/) and protein complexes from the [Complex Portal](https://www.ebi.ac.uk/complexportal/home).

Manual annotation is the direct assignment of GO terms to proteins, ncRNA and protein complexes by curators from evidence extracted during the review of published scientific literature, with an appropriate evidence code assigned to give an assessment of the strength of the evidence.  GOA files contain a mixture of manual annotation supplied by members of the Gene Ontology Consortium and computationally assigned GO terms describing gene products. Annotation type is clearly indicated by associated evidence codes and there are links to the source data.

### GO Annotations (Source Files)

There is a ReadMe.txt file that explains the different annotation files available.  The ingested Gene Annotation File (GAF) is a 17 column tab-delimited file. The file format conforms to the specifications demanded by the GO Consortium and therefore GO IDs and not GO term names are shown.

#### Biolink captured

##### Subject Concept Node (Gene)

* **biolink:Gene**
  * id (NCBIGene Entrez ID)
  * in taxon (NCBITaxon ID)
  * source (entrez)

##### Object Concept Node (Gene Ontology Terms)

* **biolink:MolecularActivity**
  * id (GO ID)
  * source (go)

* **biolink:BiologicalProcess**
  * id (GO ID)
  * source (go)

* **biolink:CellularComponent**
  * id (GO ID)
  * source (go)

##### Possible Additional Gene Ontology Term Concept Nodes?

* **biolink:Pathway**
  * id (GO ID)
  * source (go)

* **biolink:PhysiologicalProcess**
  * id (GO ID)
  * source (go)

#### Associations

* **biolink:MacromolecularMachineToMolecularActivityAssociation**:
    * id (random uuid)
    * subject (gene.id)
    * predicate (related_to)
    * object (go_term.id)
    * relation (RO:0002434)
    * provided_by (infores:goa)
    
* **biolink:MacromolecularMachineToBiologicalProcessAssociation**:
    * id (random uuid)
    * subject (gene.id)
    * predicate (participates_in)
    * object (go_term.id)
    * relation (RO:0000056)
    * provided_by (infores:goa)

* **biolink:MacromolecularMachineToCellularComponentAssociation**:
    * id (random uuid)
    * subject (gene.id)
    * predicate (located_in)
    * object (go_term.id)
    * relation (RO:0001025)
    * provided_by (infores:goa)

##### Possible Additional Gene to Gene Ontology Term Association?

* **biolink:GeneToGoTermAssociation**:
    * id (random uuid)
    * subject (gene.id)
    * predicate (related_to)
    * object (go_term.id)
    * relation (RO:0002434)
    * provided_by (infores:goa)
