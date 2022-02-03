Reactome is a free, open-source, curated and peer reviewed pathway database. Our goal is to provide intuitive bioinformatics tools for the visualization, interpretation and analysis of pathway knowledge to support basic research, genome analysis, modeling, systems biology and education.

* [Reactome bulk downloads](http://www.reactome.org/download/current/)

### Gene to Pathway

This ingest uses Reactome's gene to pathway download file, which contains all entities and only assocations between pathways and genes that are denoted in some way in the pathyways. 

#### Biolink captured

* biolink:Gene
    * id

* biolink:Pathway
    * id

* biolink:MacromolecularMachineToBiologicalProcessAssociation
    * id (random uuid)
    * subject (gene.id)
    * predicate (mentions)
    * object (pathway.id)
    * relation (participates_in)

### Chemical to Pathway

This ingest uses Reactome's chemical to pathway download file, which contains all entities and only assocations between pathways and chemicals that are denoted in some way in the pathyways. 

#### Biolink captured

* biolink:ChemicalEntity
    * id

* biolink:Pathway
    * id

* biolink:MacromolecularMachineToBiologicalProcessAssociation
    * id (random uuid)
    * subject (chemical.id)
    * predicate (mentions)
    * object (pathway.id)
    * relation (participates_in)