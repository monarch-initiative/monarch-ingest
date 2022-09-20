#
# After downloading the dicty_phenotypes.obo file from:
#
# http://dictybase.org/db/cgi-bin/dictyBase/download/download.pl?area=pheno_ontology&ID=dicty_phenotypes.obo
#
# then running the robot conversion (http://robot.obolibrary.org/convert.html) to OBO JSON, namely:
#
#    robot convert --input ./data/dictybase/dicty_phenotypes.obo --output ./data/dictybase/dicty_phenotypes.json
#
# this script can be run to extract a mapping file for the dictybase gene-to-phenotype ingest.
#

from typing import Dict
from json import load


def to_curie(uri: str):
    return uri.replace("http://purl.obolibrary.org/obo/DDPHENO_", "DDPHENO:")


with open("../../data/dictybase/dicty_phenotypes.json") as phenotype_file_json:
    dbpheno = load(phenotype_file_json)

nodes: Dict = dbpheno["graphs"][0]["nodes"]

name_to_id: Dict[str, str] = dict()

for node in nodes:

    if not ("lbl" in node and "id" in node):
        continue

    name = node["lbl"]
    uri = node["id"]
    curie = to_curie(uri)
    name_to_id[name] = curie

with open("../../data/dictybase/dicty_phenotypes.tsv", mode="w") as phenotype_file_tsv:
    print(f"name\tid", file=phenotype_file_tsv)
    for name, identifier in name_to_id.items():
        print(f"{name}\t{identifier}", file=phenotype_file_tsv)
