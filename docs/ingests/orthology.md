## Gene Orthology: functional protein association networks

Gene orthology analyses generate testable hypothesis about gene function and biological processes using experimental results from other (especially highly studied so-called 'model' species) using protein (and sometimes, simply nucleic acid level) alignments of genomic sequences.  As an (initial?) cornerstone of gene orthology data, datasets available from the Panther database are ingested into Monarch.

The [PANTHER (Protein ANalysis THrough Evolutionary Relationships) Classification System](http://www.pantherdb.org/) was designed to classify proteins (and their genes) in order to facilitate high-throughput analysis. Proteins have been classified according to:
- Family and subfamily: families are groups of evolutionarily related proteins; subfamilies are related proteins that also have the same function
- Molecular function: the function of the protein by itself or with directly interacting proteins at a biochemical level, e.g. a protein kinase
- Biological process: the function of the protein in the context of a larger network of proteins that interact to accomplish a process at the level of the cell or organism, e.g. mitosis.
- Pathway: similar to biological process, but a pathway also explicitly specifies the relationships between the interacting molecules.

The PANTHER Classifications are the result of human curation as well as sophisticated bioinformatics algorithms. Details of the methods can be found in [Mi et al. NAR 2013; Thomas et al., Genome Research 2003](http://www.genome.org/cgi/content/full/13/9/2129).

This ingest uses data derived form the current version of Panther 16.0 HMM.

* [Panther Gene Orthology bulk data downloads](http://data.pantherdb.org/ftp/pathway/current_release/)

### Source Files

#### Classifications

Contains the PANTHER 16.0 family/subfamily name, and the molecular function, biological process, and pathway classifications for every PANTHER protein family and subfamily in the current PANTHER HMM library.

* field 1...

#### Pathways

Contains regulatory and metabolic pathways, each with subfamilies and protein sequences mapped to individual pathway components.

* field 1...

#### Sequence Classifications

Contain the PANTHER family, subfamily, molecular function, biological process, and pathway classifications for the complete proteomes derived from the various genomes, indexed by species (one source file per species).  Refer to the [Sequence Classification README](http://data.pantherdb.org/ftp/sequence_classifications/current_release/README) for details.

* field 1...

#### Identifier mappings

We use the [UniProt ID mapping data data](ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/idmapping_selected.tab.gz) to map Panther protein nodes onto gene nodes with Entrez (GeneID) identifiers.

### Biolink classes and properties captured

#### Concept Nodes

* **biolink:GeneFamily**
  * id (PANTHER.FAMILY ID)
  * source (infores:panther)

* **biolink:Pathway**
  * id (PANTHER.PATHWAY)
  * source (infores:panther)

* **biolink:Gene**
  * id (NCBIGene Entrez ID)
  * in taxon (NCBITaxon ID)
  * source (infores:entrez)

#### Possible Associations

##### Gene to Pathway

* **biolink:MacromolecularMachineToBiologicalProcessAssociation**:
    * id (random uuid)
    * subject (gene.id)
    * predicate (participates_in)
    * object (pathway.id)
    * relation (RO:0000056)
    * provided_by (infores:panther)

##### Gene to Gene Family

* **biolink:GeneToGeneFamilyAssociation**:
    * id (random uuid)
    * subject (gene.id)
    * predicate (member_of)
    * object (gene_family.id)
    * relation (RO:0002350)
    * provided_by (infores:panther)

##### Gene to Gene Homology

* **biolink:GeneToGeneHomologyAssociation**:
    * id (random uuid)
    * subject (gene.id)
    * predicate (orthologous to)
    * object (gene.id)
    * relation (RO:HOM0000017)
    * provided_by (infores:panther)

This relationship can be inferred from common PANTHER.FAMILY membership?

##### Gene to Gene Ontology Term (also available in Panther)?

* **biolink:GeneToGoTermAssociation**:
    * id (random uuid)
    * subject (gene.id)
    * predicate (*)
    * object (go_term.id)
    * relation (RO:0002434)
    * provided_by (infores:goa)

(*) Note that the specific predicate used here should depend on GO Annotation qualifier for the given gene.