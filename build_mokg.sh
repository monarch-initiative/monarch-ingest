rm output/transform_output/* -rf
rm data/* -rf
poetry run ingest download --ingest_file src/monarch_ingest/ingest_configs/mokg_downloads.txt
bash scripts/after_download.sh
poetry run ingest transform --phenio
poetry run ingest transform --ingest_file src/monarch_ingest/ingest_configs/mokg_transforms.txt
poetry run ingest merge --kg-name mokg

#This is a command to convert the KGX output found in output/mokg.tar.gz into RDF output.
#This is taken from https://github.com/monarch-initiative/monarch-ingest/blob/3d2b0b3693a021d7660214bcd81abc4409f8efe2/scripts/kgx_transforms.sh#L12
#poetry run kgx transform -i tsv -c tar.gz -f nt -d gz -o output/monarch-kg.nt.gz output/monarch-kg.tar.gz

cp output/mokg.tar.gz /projects/stars/var/data_services/mokg/mokg.tar.gz