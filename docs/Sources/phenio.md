# PHENIO

PHENIO is an ontology for accessing and comparing knowledge concerning phenotypes across species and genetic backgrounds.

Phenio provides the "semantic backbone" of the Monarch Knowledge Graph.  
Designed as an application ontology, PHENIO integrates a variety of ontological concepts, in particular
the "core entities" in the Monarch Knowledge Graph (KG), including diseases, phenotypes and anatomical entities.

Note that while forming an integral part of the Monarch KG, PHENIO does not have a "Koza Ingest" configuration like all the other sources, 
but is instead ingested into Monarch KG straight via a `OWL -> obographs -> KGX` transform.

## Sources

PHENIO integrates several different types of hierarchical relationships from a variety of sources.

These include:
* Chemical entities and relationships from [CHEBI](https://www.ebi.ac.uk/chebi/)
* Disease entities and relationships from [MONDO](https://mondo.monarchinitiative.org/)
* Abnormal phenotypes of humans ([HPO](https://hpo.jax.org/app/)), mouse and other mammalian species ([MPO](https://www.informatics.jax.org/vocab/mp_ontology)), the nematode worm Caenorhabditis elegans ([WBBT](http://www.obofoundry.org/ontology/wbphenotype.html)), and zebrafish ([ZFA](http://www.obofoundry.org/ontology/zfa.html)).

[A full list of files used in the construction of PHENIO is available here.](https://monarch-initiative.github.io/phenio/odk-workflows/RepositoryFileStructure/)

## More Information
For more information, see:

- [NCATS Translater Phenio Overview](https://github.com/NCATSTranslator/Translator-All/wiki/phenio)
- [KGHub Phenio](https://github.com/Knowledge-Graph-Hub/kg-phenio)  
- [Monarch Phenio](https://github.com/monarch-initiative/phenio)
- [Documentation](https://monarch-initiative.github.io/phenio/)

## Source Code

https://github.com/monarch-initiative/phenio
