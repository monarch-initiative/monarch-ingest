# BioGRID

BioGRID is a database of Protein, Genetic and Chemical Interactions, a biomedical interaction repository with data compiled through comprehensive curation efforts. The current index searches thousands of publications extracting millions of protein and genetic interactions, thousands of chemical interactions and over a million post translational modifications from major model organism species.

### Source File

Data columns (defined [here](https://wiki.thebiogrid.org/doku.php/psi_mitab_file)) in the [Bulk BioGrid data file](https://downloads.thebiogrid.org/File/BioGRID/Release-Archive/BIOGRID-4.4.226/BIOGRID-ALL-4.4.226.mitab.zip) are as follows:

1. ID Interactor A
2. ID Interactor B
3. Alt IDs Interactor A
4. Alt IDs Interactor B
5. Aliases Interactor A
6. Aliases Interactor B
7. Interaction Detection Method
8. Publication 1st Author
9. Publication Identifiers
10. Taxid Interactor A
11. Taxid Interactor B
12. Interaction Types
13. Source Database
14. Interaction Identifiers
15. Confidence Values

with a typical row looking like:

1. entrez gene/locuslink:6416
2. entrez gene/locuslink:2318
3. biogrid:112315|entrez gene/locuslink:MAP2K4|uniprot/swiss-prot:P45985|refseq:NP_003001|refseq:NP_001268364
4. biogrid:108607|entrez gene/locuslink:FLNC|uniprot/swiss-prot:Q14315|refseq:NP_001120959|refseq:NP_001449
5. entrez gene/locuslink:JNKK(gene name synonym)|entrez gene/locuslink:JNKK1(gene name synonym)|entrez gene/locuslink:MAPKK4(gene name synonym)|entrez gene/locuslink:MEK4(gene name synonym)|entrez gene/locuslink:MKK4(gene name synonym)|entrez gene/locuslink:PRKMK4(gene name synonym)|entrez gene/locuslink:SAPKK-1(gene name synonym)|entrez gene/locuslink:SAPKK1(gene name synonym)|entrez gene/locuslink:SEK1(gene name synonym)|entrez gene/locuslink:SERK1(gene name synonym)|entrez gene/locuslink:SKK1(gene name synonym)
6. entrez gene/locuslink:ABP-280(gene name synonym)|entrez gene/locuslink:ABP280A(gene name synonym)|entrez gene/locuslink:ABPA(gene name synonym)|entrez gene/locuslink:ABPL(gene name synonym)|entrez gene/locuslink:FLN2(gene name synonym)|entrez gene/locuslink:MFM5(gene name synonym)|entrez gene/locuslink:MPD4(gene name synonym)
7. psi-mi:"MI:0018"(two hybrid)
8. "Marti A (1997)"
9. pubmed:9006895
10. taxid:9606
11. taxid:9606
12. psi-mi:"MI:0407"(direct interaction)
13. psi-mi:"MI:0463"(biogrid)
14. biogrid:103
15. <empty/>

(note: column 15 of this row doesn't report a confidence value).

The BioGRID ingest only uses columns 1, 2 and 9 to generate its output

### Biolink classes and properties captured

#### Concept Nodes

The statement 'subject' (column 1) and 'object' (column 2) nodes are both genes:

* **biolink:Gene**
  * id (NCBIGene Entrez ID)

#### Associations

* **biolink:PairwiseGeneToGeneInteraction**:
    * id (random uuid)
    * subject (gene.id)
    * predicate (interacts_with)
    * object (gene.id)
    * has_evidence (ECO codes)
    * publications (LIST[Pubmed ID])
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source ("infores:biogrid")

## Citations

### Most Recent

* Oughtred R, Rust J, Chang C, Breitkreutz BJ, Stark C, Willems A, Boucher L, Leung G, Kolas N, Zhang F, Dolma S, Coulombe-Huntington J, Chatr-Aryamontri A, Dolinski K, Tyers M. **The BioGRID database: A comprehensive biomedical resource of curated protein, genetic, and chemical interactions.** [_Protein Sci. 2020 Oct 18_](https://doi.org/10.1002/pro.3978). [PMID:33070389](https://pubmed.ncbi.nlm.nih.gov/33070389/)

### Original

* Stark C, Breitkreutz BJ, Reguly T, Boucher L, Breitkreutz A, Tyers M. **Biogrid: A General Repository for Interaction Datasets.** _Nucleic Acids Res. Jan 1, 2006; 34:D535-9_; [PMID:16381927](http://www.ncbi.nlm.nih.gov/pubmed/16381927).