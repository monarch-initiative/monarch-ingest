import sh

ssh_command = "compute ssh --zone us-central1-a monarch-v3-dev-solr"
vm_command = '''
sudo echo ${EUID}
'''
# cd /srv/monarch-v3 && \\
# rm solr.tar.gz && \\
# wget https://data.monarchinitiative.org/monarch-kg-dev/latest/solr.tar.gz && \\
# tar -xzf solr.tar.gz && \\
# rm solr.tar.gz && \\
# docker service update --force monarch-v3_solr

sh.gcloud(
    *ssh_command.split(),
    f"--command={vm_command}",
    _out=print
)
