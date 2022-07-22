# Phenio - Phenomics Integrated Ontology

Phenio provides the "semantic backbone" of the Monarch Knowledge Graph. 
Designed as an application ontology, it comprises a variety of ontological concepts, in particular all the ones 
that are "core entities" in the Monarch Knowledge Graph (KG), such as diseases, phenotypes and anatomical entities.

Here, we document how Phenio "flows" through the system, from how it is created to how it is utilised. Note that while forming
an integral part of the Monarch KG, it does not have a  "Koza Ingest" configuration like all the other sources, but is
instead ingested into Monarch KG straight via a OWL->obographs->KGX transform.

Under construction, materials:

- https://github.com/monarch-initiative/monarch-ingest/blob/91eaacaab23941bb58130c52040c5e118f2c1a21/monarch_ingest/cli_utils.py#L93
- https://docs.google.com/presentation/d/1YEYMeP0vBpV52ezDDJfn2xmOOEGROlOT-CXjEk6LIkA/edit#slide=id.p
