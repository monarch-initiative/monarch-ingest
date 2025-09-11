"""
This script is used to update the solr service in the monarch-v3-dev cluster.
It stops the solr service, downloads the latest solr.tar.gz, and starts the solr service.

This could be a bash script, but Python allows for easier string manipulation,
and better encapsulation of the commands to be executed inside the VM.
"""

import os
import sh

# Stop the solr service from the manager node
sh.gcloud(
    *"compute ssh --zone us-central1-a monarch-v3-dev-manager".split(),
    "--",
    "sudo docker service scale monarch-v3_solr=0",
)


# Download the latest solr.tar.gz on the solr node
ssh_command = "compute ssh --zone us-central1-a monarch-v3-dev-solr"
vm_command = """
cd /srv/monarch-v3
sudo wget https://data.monarchinitiative.org/monarch-kg-dev/latest/solr.tar.gz -O solr.tar.gz
sudo rm -rf data
sudo tar -xzf solr.tar.gz
sudo chgrp -R 8983 data
sudo chmod -R g+w data
"""

sh.gcloud(*ssh_command.split(), f"--command={vm_command}", _out=print)


# Start the solr service from the manager node
sh.gcloud(
    *"compute ssh --zone us-central1-a monarch-v3-dev-manager".split(),
    "--",
    "sudo docker service scale monarch-v3_solr=1",
)


RELEASE = os.environ["RELEASE"]
MONARCH_KG_VERSION = RELEASE
MONARCH_API_VERSION = "latest"
MONARCH_KG_SOURCE = "https://data.monarchinitiative.org/monarch-kg-dev/" + MONARCH_KG_VERSION

sh.gcloud(
    *"compute ssh --zone us-central1-a monarch-v3-dev-manager".split(),
    "--",
    f"sudo docker service update monarch-v3_api --env-add MONARCH_KG_VERSION={MONARCH_KG_VERSION} --env-add MONARCH_API_VERSION={MONARCH_API_VERSION} --env-add MONARCH_KG_SOURCE={MONARCH_KG_SOURCE}",
)
