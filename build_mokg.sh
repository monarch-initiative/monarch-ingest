rm output/transform_output/* -rf
rm data/* -rf
poetry run ingest download --ingest_file src/monarch_ingest/ingest_configs/mokg_downloads.yaml
bash scripts/after_download.sh
poetry run ingest transform --phenio
poetry run ingest transform --ingest_file src/monarch_ingest/ingest_configs/mokg_transforms.yaml
poetry run ingest merge --kg-name mokg

#This is a command to convert the KGX output found in output/mokg.tar.gz into RDF output.
#This is taken from https://github.com/monarch-initiative/monarch-ingest/blob/3d2b0b3693a021d7660214bcd81abc4409f8efe2/scripts/kgx_transforms.sh#L12
#poetry run kgx transform -i tsv -c tar.gz -f nt -d gz -o output/monarch-kg.nt.gz output/monarch-kg.tar.gz
#poetry run kgx transform -i tsv -c tar.gz -f nt -d gz -o output/monarch-kg.nt.gz output/monarch-kg.tar.gz

#cp output/mokg.tar.gz /projects/stars/var/data_services/mokg/mokg.tar.gz
#poetry run kgx transform --input-format tsv --input-compression gz --output output/mokg-json.gz --output-format jsonl --output-compression gz output/mokg.tar.gz

#poetry run kgx transform --input-format tsv --input-compression tar.gz --output output/mokg.nt.gz --output-format nt --output-compression gz output/mokg.tar.gz

#poetry run kgx transform --input-format tsv --input-compression tar.gz --output output/mokg-json.gz --output-format jsonl --output-compression gz output/mokg.tar.gz
poetry run kgx transform --input-format tsv --input-compression tar.gz --output output/mokg --output-format jsonl output/mokg.tar.gz
tar -acf output/mokg-jsonl.tar.gz output/mokg_nodes.jsonl output/mokg_edges.jsonl 

cp output/mokg-jsonl.tar.gz /projects/stars/var/data_services/mokg/mokg-jsonl.tar.gz

sbatch slurm_job_dir/sync_mokg_output_to_neo4j.sbatch
