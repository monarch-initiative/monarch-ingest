import json
import requests
from pathlib import Path

from loguru import logger
from pprint import pprint as pp


OUTDIR = Path(__file__).parent.parent / "output" / "transform_output"

# Modular ingests to download output from GitHub releases
ingests = {
    # 'alliance-variant-allele-ingest'
    # 'ncbi-gene',
    "alliance-disease-association-ingest": ["alliance_disease_edges"],
    "clingen-ingest": ["clingen_variant_nodes", "clingen_variant_edges"],
    "clinvar-ingest": ["clinvar_variant_nodes", "clinvar_variant_edges"],
}
# url="https://api.github.com/repos/monarch-initiative/monarch-ingest/releases",

for key, value in ingests.items():
    url = f"https://api.github.com/repos/monarch-initiative/{key}/releases/latest"

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(
            f"\n\tFailed to get latest release from {url}\n\tStatus: {response.status_code} - {response.text}"
        )
    data = json.loads(response.text)

    files_to_download = [
        asset["browser_download_url"] for asset in data["assets"] if asset["name"].split(".")[0] in value
    ]
    pp(files_to_download)

    for file in files_to_download:
        Path(OUTDIR).mkdir(parents=True, exist_ok=True)
        response = requests.get(file)
        if response.status_code != 200:
            # TODO: raise exception? log warning/error?
            # logger.error(f"Failed to download {file}: {response.text}")
            # i.e. do we want ingest-all to fail if not absolutely correct?
            raise Exception(f"Failed to download {file}: {response.text}")
        with open(f"{OUTDIR}/{file.split('/')[-1]}", "wb") as out_fn:
            out_fn.write(response.content)
