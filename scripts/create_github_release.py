import argparse
import os
import requests
from pathlib import Path


DIR = Path(__file__).parent.parent / "output"
GH_TOKEN = os.environ["GH_RELEASE_TOKEN"]
UPLOAD_FILES = [
    "monarch-kg.tar.gz",
    "monarch-kg.duckdb",
    "merged_graph_stats.yaml",
    "qc_report.yaml",
    "metadata.yaml",
]


def create_release(kg_version: str):
    print(f"Creating release for {kg_version}")
    response = requests.post(
        url="https://api.github.com/repos/monarch-initiative/monarch-ingest/releases",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GH_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={
            "tag_name": kg_version,
            "target_commitish": "main",
            "name": kg_version,
            # "body": "body",
            "draft": True,
            "prerelease": False,
            "generate_release_notes": True,
        },
    )
    if response.status_code != 201:
        raise Exception(f"Failed to create release: {response.text}")
    release_id = response.json()["id"]
    print(f"Release {kg_version} created with id {release_id}")
    return release_id


def upload_assets(kg_version: str, release_id: str, files: list):
    print(f"\nUploading assets for {kg_version}")
    for file in files:
        upload_name = file.split("/")[-1]
        print(f"Uploading {file} as {upload_name}...")
        with open(f"{DIR}/{file}", "rb") as f:
            response = requests.post(
                url=f"https://uploads.github.com/repos/monarch-initiative/monarch-ingest/releases/{release_id}/assets?name={upload_name}",
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {GH_TOKEN}",
                    "X-GitHub-Api-Version": "2022-11-28",
                    "Content-Type": "application/octet-stream",
                },
                data=f,
            )
            if response.status_code != 201:
                raise Exception(f"Failed to upload asset {file}: {response.text}")
            print(f"{file} uploaded successfully")


def main(kg_version: str):
    release_id = create_release(kg_version)
    upload_assets(kg_version, release_id, UPLOAD_FILES)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--kg-version", type=str, help="KG Version to create tag and release for, ex. 2022-11-28")
    args = parser.parse_args()
    main(args.kg_version)
