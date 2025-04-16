This readme is specific to the multiomics-approvals-and-trials-edges branch

# (Quickly) loading Multiomics KP edges (and drug nodes) for clinical trial & drug approval edges

### To avoid having to re-run all of the transforms, fetch the transformed output
gsutil -m cp "gs://data-public-monarchinitiative/monarch-kg-dev/2025-04-15/transform_output/*" output/transform_output/

### download the multiomics files & sssom & relation graph 
poetry run ingest download --ingest multiomics
poetry run ingest download --ingest mapping
poetry run ingest download --ingest phenio

### ugly awk filtering to get drug nodes (as defined in after_download.sh)
awk 'NR == 1 || $3 == "biolink:ChemicalEntity" || $3 == "biolink:SmallMolecule" || $3 == "biolink:MolecularMixture"' data/multiomics-kp/clinical_trials_kg_v2.7.2_nodes.tsv > data/multiomics-kp/clinical_trials_kg_v2.7.2_chemical_nodes.tsv
awk 'NR == 1 || $3 == "biolink:ChemicalEntity" || $3 == "biolink:SmallMolecule" || $3 == "biolink:MolecularMixture"' data/multiomics-kp/drug_approvals_kg_v0.3.7_nodes.tsv > data/multiomics-kp/drug_approvals_kg_v0.3.7_chemical_nodes.tsv

### also run the ugly hacks to process the relation graph file and tweak prefixes in MONDO sssom 

gunzip data/monarch/phenio-relation-graph.tsv.gz 
awk '{ if ($2 == "rdfs:subClassOf" || $2 == "BFO:0000050" || $2 == "UPHENO:0000001") { print } }' data/monarch/phenio-relation-graph.tsv > data/monarch/phenio-relation-filtered.tsv

#gsed on a mac, sed on linux
gsed -i 's/\torphanet.ordo\:/\tOrphanet\:/g' data/monarch/mondo.sssom.tsv
gsed -i 's@mesh:@MESH:@g' data/monarch/mondo.sssom.tsv


### Merge the KG 
poetry run ingest merge

### closurizer to make the duckdb database 
poetry run ingest closure 
