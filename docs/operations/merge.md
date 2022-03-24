## Notes on merging

if necessary:
```bash=
git clone https://github.com/monarch-initiative/monarch-ingest.git
cd monarch-ingest
pip3 install poetry
poetry install
```

Download the tsv files from the output bucket

```bash=
mkdir output
gsutil cp gs://monarch-ingest/kgx/*.tsv kgx/
```

Start a neo4j docker container to write to

```bash=
sudo mkdir -p /neo4j/logs
sudo mkdir -p /neo4j/data
docker run \
    --name monarch_ingest_neo4j \
    -p7474:7474 -p7687:7687 \
    -d \
    -v $HOME/neo4j/data:/neo4j/data \
    -v $HOME/neo4j/logs:/neo4j/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/admin \
    neo4j:4.4.4-community
```

Run the merge command, set -p to an appropriate number of CPUs

```bash=
poetry run kgx merge --merge-config merge.yaml -p 8
```
