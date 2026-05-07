rm output/transform_output/* -rf
rm data/* -rf
uv run ingest download --ingest_file src/monarch_ingest/ingest_configs/mokg_downloads.txt
uv run ingest download-release-metadata
bash scripts/after_download.sh
uv run ingest transform --phenio
uv run ingest transform --ingest_file src/monarch_ingest/ingest_configs/mokg_transforms.txt
uv run ingest merge --kg-name mokg
uv run ingest build-receipt --kg-name mokg

#This is a command to convert the KGX output found in output/mokg.tar.gz into RDF output.
#This is taken from https://github.com/monarch-initiative/monarch-ingest/blob/3d2b0b3693a021d7660214bcd81abc4409f8efe2/scripts/kgx_transforms.sh#L12
#uv run kgx transform -i tsv -c tar.gz -f nt -d gz -o output/monarch-kg.nt.gz output/monarch-kg.tar.gz
