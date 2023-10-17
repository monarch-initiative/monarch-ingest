# BGee

Bgee is a database for retrieval and comparison of gene expression patterns across multiple animal species, produced from multiple data types (bulk RNA-Seq, single-cell RNA-Seq, Affymetrix, in situ hybridization, and EST data) and from multiple data sets (including GTEx data).


## [Gene Expression](#gene)

This is the full data model of the Bgee simple gene expression file; however, not all fields are currently used in the current ingest.
Files are named by Species ID.

* "Gene name"
* Anatomical entity ID
* "Anatomical entity name"
* Expression
* Call quality
* FDR
* Expression score
* Expression rank

__**Biolink Captured**__

* biolink:GeneToExpressionSiteAssociation
    * id (random uuid, generated)
    * subject (`Gene ID`)
    * predicates (biolink:expressed_in, constant)
    * object (`Anatomical entity ID`)
    * aggregating_knowledge_source (["infores:monarchinitiative", "infores:bgee"])

__**Decisions and Discussion**__

We elected to use the simple gene expression file for ease of use and because the advanced doesn't contain much more data we are likely to use.
We could potentially import `has evidence` from the advanced file comparing `Affimetrix expression` and `RNA-Seq expression` but this doesn't seem valuable at this time.
Stage and Strain information is also available in all_conditions file. We have elected to not import the stage information due to multiple duplicate edges based on strain.


## Citation

"Bastian FB, Roux J, Niknejad A, Comte A, Fonseca Costa SS, Mendes de Farias T, Moretti S, Parmentier G, Rech de Laval V, Rosikiewicz M, Wollbrett J, Echchiki A, Escoriza A, Gharib W, Gonzales-Porta M, Jarosz Y, Laurenczy B, Moret P, Person E, Roelli P, Sanjeev K, Seppey M, Robinson-Rechavi M. 
The Bgee suite: integrated curated expression atlas and comparative transcriptomics in animals
in Nucleic Acids Research, Volume 49, Issue D1, 8 January 2021, Pages D831-D847"