rm output/transform_output/* -rf
rm data/* -rf
poetry run ingest download --ingest_file src/monarch_ingest/ingest_configs/mokg_downloads.yaml
bash scripts/after_download.sh
poetry run ingest transform --phenio
poetry run ingest transform --ingest_file src/monarch_ingest/ingest_configs/mokg_transforms.yaml

#This makes the DuckDB file Now
poetry run ingest merge --kg-name mokg

poetry run ingest neo4j-csv --name mokg --duckdb output/mokg.duckdb

