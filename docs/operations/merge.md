## Notes on merging

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
