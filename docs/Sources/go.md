# Gene Ontology (GO) Annotation Database

The Gene Ontology Annotation Database compiles high-quality [Gene Ontology (GO)](http://www.geneontology.org/) annotations to proteins in the [UniProt Knowledgebase (UniProtKB)](https://www.uniprot.org/), RNA molecules from [RNACentral](http://rnacentral.org/) and protein complexes from the [Complex Portal](https://www.ebi.ac.uk/complexportal/home).

Manual annotation is the direct assignment of GO terms to proteins, ncRNA and protein complexes by curators from evidence extracted during the review of published scientific literature, with an appropriate evidence code assigned to give an assessment of the strength of the evidence.  GOA files contain a mixture of manual annotation supplied by members of the Gene Ontology Consortium and computationally assigned GO terms describing gene products. Annotation type is clearly indicated by associated evidence codes and there are links to the source data.

## [GO Annotations](#go_annotation)

There is a ReadMe.txt file that explains the different annotation files available.  The ingested Gene Annotation File (GAF) is a 17 column tab-delimited file. The file format conforms to the specifications demanded by the GO Consortium and therefore GO IDs and not GO term names are shown.

__**Biolink captured**__

##### Subject Concept Node (Gene)

* **biolink:Gene**
  * id (NCBIGene Entrez ID)

##### Object Concept Node (Gene Ontology Terms)

* **biolink:MolecularActivity**
  * id (GO ID)

* **biolink:BiologicalProcess**
  * id (GO ID)

* **biolink:CellularComponent**
  * id (GO ID)

##### Additional Gene Ontology Term Concept Nodes for possible use?

* **biolink:Pathway**
  * id (GO ID)

* **biolink:PhysiologicalProcess**
  * id (GO ID)

__**Associations**__

* **biolink:FunctionalAssociation**
    * id (random uuid)
    * subject (gene.id)
    * predicate (related_to)
    * object (go_term.id)
    * negated
    * has_evidence
    * publications
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source

OR

* **biolink:MacromolecularMachineToMolecularActivityAssociation**:
    * id (random uuid)
    * subject (gene.id)
    * predicate (related_to)
    * object (go_term.id)
    * negated
    * has_evidence
    * publications
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source
    
* **biolink:MacromolecularMachineToBiologicalProcessAssociation**:
    * id (random uuid)
    * subject (gene.id)
    * predicate (participates_in)
    * object (go_term.id)
    * negated
    * has_evidence
    * publications
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source

* **biolink:MacromolecularMachineToCellularComponentAssociation**:
    * id (random uuid)
    * subject (gene.id)
    * predicate (located_in)
    * object (go_term.id)
    * negated
    * has_evidence
    * publications
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source

__**Possible Additional Gene to Gene Ontology Term Association?**__

* **biolink:GeneToGoTermAssociation**:
    * id (random uuid)
    * subject (gene.id)
    * predicate (related_to)
    * object (go_term.id)
    * negated
    * has_evidence
    * publications
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source

## Citation

Ashburner et al. Gene ontology: tool for the unification of biology. Nat Genet. 2000 May;25(1):25-9.  The Gene Ontology Consortium. The Gene Ontology knowledgebase in 2023. Genetics. 2023 May 4;224(1):iyad031