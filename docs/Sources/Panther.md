## Panther Gene Orthology

Gene orthology analyses generate testable hypothesis about gene function and biological processes using experimental results from other (especially highly studied so-called 'model' species) using protein (and sometimes, simply nucleic acid level) alignments of genomic sequences.  The source of gene orthology data for this ingest is from the  [PANTHER (Protein ANalysis THrough Evolutionary Relationships) Classification System](http://www.pantherdb.org/). Panther was designed to classify proteins (and their genes) in order to facilitate high-throughput analysis. Proteins have been classified according to:
- _Family and subfamily:_ families are groups of evolutionarily related proteins; subfamilies are related proteins that also have the same function
- _Molecular function:_ the function of the protein by itself or with directly interacting proteins at a biochemical level, e.g. a protein kinase
- _Biological process:_ the function of the protein in the context of a larger network of proteins that interact to accomplish a process at the level of the cell or organism, e.g. mitosis.
- _Pathway:_ similar to biological process, but a pathway also explicitly specifies the relationships between the interacting molecules.

The PANTHER Classifications are the result of human curation as well as sophisticated bioinformatics algorithms. Details of the methods can be found in [Mi et al. NAR 2013; Thomas et al., Genome Research 2003](http://www.genome.org/cgi/content/full/13/9/2129).

This ingest uses data derived form the current version (release 16.0) of the Panther Hidden Markov Model (HMM).

* [Panther Gene Orthology bulk data downloads](http://data.pantherdb.org/ftp/pathway/current_release/)

There are various cross-sections of the Panther database which remain be covered by this ingest (Note: **T.B.D** means "To Be Done")

### Status of Panther Ingest

The first iteration of this dataset (committed March 2022) focuses on [Reference Genome Gene-to-Gene Orthology Relationships](#reference-genome-gene-to-gene-orthology-relationships). Additional Panther associations (protein (sub)family pathways, sequences, _etc_, as generally described below) may be added at a later date.

### Reference Genome Gene-to-Gene Orthology Relationships

Contains the Reference Genomes' Gene-to-Gene Ortholog mappings from Panther analyses.


- _Source File:_ [RefGenomeOrthologs.tar.gz](http://data.pantherdb.org/ftp/ortholog/current_release/RefGenomeOrthologs.tar.gz)

#### Panther Data Model of RefGenomeOrthologs

| Data Field | Content                                     | 
|------------|---------------------------------------------| 
| Gene       | species1 &#124; DB=id1 &#124; protdb=pdbid1|
| Ortholog   | species2 &#124; DB=id2 &#124; protdb=pdbid2| 
| Type of ortholog   | [LDO, O, P, X ,LDX]  see [README](http://data.pantherdb.org/ftp/ortholog/current_release/README). | 
| Common ancestor for the orthologs   | taxon name of common ancestor|
| Panther Ortholog ID   | Panther (sub)family identifier| 

The `DB=id#` fields - where DB == database namespace and id# is the object identifier - are directly translated, by internal namespace mapping, into gene CURIEs.

The `species#` are abridged labels currently filtered and mapped onto NCBI Taxon identifiers, using an hard-coded dictionary.

#### Biolink classes and properties captured

- **biolink:Gene**
  * id (NCBIGene Entrez ID)
  * in taxon (NCBITaxon ID)
  * source (infores:panther) 

Note that the Gene `source` is currently given as Panther, although the real source of a Gene identifier is given by its CURIE namespace.


- **biolink:GeneToGeneHomologyAssociation**
  * id (random uuid)
  * subject (gene.id)
  * predicate (orthologous to)
  * object (gene.id)
  * relation (RO:HOM0000017)
  * provided_by (infores:panther)

### Protein Family and Subfamily Classifications - T.B.D.

Contains the PANTHER 16.0 family/subfamily name, with molecular function, biological process, and pathway classifications for every PANTHER protein family and subfamily in the current PANTHER HMM library.

- _Source File:_ http://data.pantherdb.org/ftp/hmm_classifications/current_release/PANTHER16.0_HMM_classifications

- _Biolink classes and properties captured:_

   - **biolink:GeneFamily**
     * id (PANTHER.FAMILY ID)
     * source (infores:panther)

   - **biolink:MolecularActivity**
     * id (GO ID)
     * source (go)

   - **biolink:BiologicalProcess**
     * id (GO ID)
     * source (go)

   - **biolink:Pathway**
     * id (PANTHER.PATHWAY)
     * source (infores:panther)

   - **biolink:GeneFamilyToMolecularFunctionAssociation**
     * id (random uuid)
     * subject (gene_family.id)
     * predicate (enables)
     * object (go_term.id)
     * relation (RO:0002327)
     * provided_by (infores:panther)

     - **biolink:GeneFamilyToBiologicalProcessAssociation**
       * id (random uuid)
       * subject (gene_family.id)
       * predicate (involved_in)
       * object (go_term.id)
       * relation (RO:0002331)
       * provided_by (infores:panther)

     - **biolink:GeneFamilyToPathwayAssociation**
       * id (random uuid)
       * subject (gene_family.id)
       * predicate (involved_in)
       * object (pathway.id)
       * relation (RO:0002331)
       * provided_by (infores:panther)

### Pathways - T.B.D.

Contains regulatory and metabolic pathways, each with subfamilies and protein sequences mapped to individual pathway components.

- _Source File:_ http://data.pantherdb.org/ftp/pathway/current_release/SequenceAssociationPathway3.6.5.txt
  local_name: data/orthology/pathways.tsv

- _Biolink classes and properties captured:_

    - **biolink:GeneFamily**
      * id (PANTHER.FAMILY ID)
      * source (infores:panther)

    - **biolink:Gene**
      * id (NCBIGene Entrez ID)
      * in taxon (NCBITaxon ID)
      * source (infores:entrez)

    - **biolink:Pathway**
      * id (PANTHER.PATHWAY)
      * source (infores:panther)

    - **biolink:GeneToPathwayAssociation**
      * id (random uuid)
      * subject (gene.id)
      * predicate (involved_in)
      * object (pathway.id)
      * relation (RO:0002331)
      * provided_by (infores:panther)

    - **biolink:GeneFamilyToPathwayAssociation**
      * id (random uuid)
      * subject (gene_family.id)
      * predicate (involved_in)
      * object (pathway.id)
      * relation (RO:0002331)
      * provided_by (infores:panther)

### Sequence Classifications - T.B.D.

Sequence Classifications files contain the PANTHER family, subfamily, molecular function, biological process, and pathway classifications for the complete proteomes derived from the various genomes, indexed by species (one source file per species).  Refer to the [Sequence Classification README](http://data.pantherdb.org/ftp/sequence_classifications/current_release/README) for details. 

Only a subset of the available species will be ingested into Monarch at this time, currently: human, mouse, rat, zebrafish, fruit fly, nematode, fission yeast and budding ("baker's") yeast.

- _Source File Directory:_ http://data.pantherdb.org/ftp/sequence_classifications/current_release/PANTHER_Sequence_Classification_files/

- _Biolink classes and properties captured:_

   - **biolink:Gene**
     * id (PANTHER.FAMILY ID)
     * source (infores:panther)

   - **biolink:GeneFamily**
     * id (PANTHER.FAMILY ID)
     * source (infores:panther)

   - **biolink:MolecularActivity**
     * id (GO ID)
     * source (go)

   - **biolink:BiologicalProcess**
     * id (GO ID)
     * source (go)

   - **biolink:Pathway**
     * id (PANTHER.PATHWAY)
     * source (infores:panther)

   - **biolink:GeneToGeneFamilyAssociation**:
     * id (random uuid)
     * subject (gene.id)
     * predicate (member_of)
     * object (gene_family.id)
     * relation (RO:0002350)
     * provided_by (infores:panther)

   - **biolink:MacromolecularMachineToMolecularActivityAssociation**:
     * id (random uuid)
     * subject (gene.id)
     * predicate (enables)
     * object (go_term.id)
     * relation (RO:0002327)
     * provided_by (infores:panther)
    
   - **biolink:MacromolecularMachineToBiologicalProcessAssociation**:
     * id (random uuid)
     * subject (gene.id)
     * predicate (involved_in)
     * object (go_term.id)
     * relation (RO:0002331)
     * provided_by (infores:panther)

   - **biolink:GeneToPathwayAssociation**
     * id (random uuid)
     * subject (gene.id)
     * predicate (involved_in)
     * object (pathway.id)
     * relation (RO:0002331)
     * provided_by (infores:panther)
