"""Aggregate per-ingest `release-metadata.yaml` files into a monarch-kg build receipt.

Each per-ingest file (a `kozahub_metadata_schema:ReleaseMetadata`) is rewritten
as a nested `Release` (per the recursive shape in kozahub-metadata-schema): the
top-level `source`/`source_version` becomes `id`/`version`. Leaf upstream
`SourceVersion` records already use `id`/`version` and slot in unchanged.

Cross-ingest version disagreements (same `infores:` consumed at different
versions across contributing ingests) are surfaced at the top level of the
aggregated document.
"""

from __future__ import annotations

import datetime
import hashlib
from collections import defaultdict
from pathlib import Path

import yaml


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_per_ingest_metadata(input_dir: str | Path) -> list[dict]:
    files = sorted(Path(input_dir).glob("*.yaml"))
    return [yaml.safe_load(p.read_text()) for p in files]


_NESTED_KEY_ORDER = (
    "id",
    "version",
    "transform_version",
    "biolink_version",
    "build_version",
    "generated_at",
    "sources",
    "artifacts",
    "tools",
)


def to_nested_release(per_ingest: dict) -> dict:
    """Promote a per-ingest `ReleaseMetadata` doc to a nested `Release`.

    Renames `source` → `id` and `source_version` → `version`; everything else
    (transform_version, biolink_version, build_version, generated_at, sources,
    artifacts, tools) is already in the right shape.
    """
    promoted = dict(per_ingest)
    promoted["id"] = promoted.pop("source")
    if "source_version" in promoted:
        promoted["version"] = promoted.pop("source_version")

    ordered = {k: promoted[k] for k in _NESTED_KEY_ORDER if k in promoted}
    for k, v in promoted.items():
        if k not in ordered:
            ordered[k] = v
    return ordered


# `version_method` values whose "version" is a moving snapshot timestamp
# (not a stable release identifier). Skew across ingests on these methods is
# expected — they're flagged as `version_drift` rather than `disagreements`.
ROLLING_VERSION_METHODS = frozenset({
    "http_last_modified",
    "github_branch_head",
    "max_published_date",
})


def find_disagreements(per_ingest_docs: list[dict]) -> tuple[list[dict], list[dict]]:
    """Bucket cross-ingest version mismatches by source stability.

    Returns `(disagreements, version_drift)`:
    - `disagreements`: any source seen at multiple versions where at least one
      ingest used a tagged-release `version_method` — likely a real conflict.
    - `version_drift`: mismatches across rolling sources only (e.g. NCBI's
      `gene_info.gz` Last-Modified header advancing between fetches) — expected.
    """
    by_source: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for doc in per_ingest_docs:
        ingest = doc.get("source")
        for src in doc.get("sources") or []:
            sid = src.get("id")
            if sid:
                by_source[sid].append((ingest, src.get("version"), src.get("version_method")))

    disagreements: list[dict] = []
    drift: list[dict] = []
    for sid, observations in sorted(by_source.items()):
        versions = {v for _, v, _ in observations}
        if len(versions) <= 1:
            continue
        methods = {m for _, _, m in observations}
        record = {
            "id": sid,
            "versions_observed": sorted(v for v in versions if v is not None),
            "by_ingest": {ingest: ver for ingest, ver, _ in observations},
        }
        all_rolling = methods <= ROLLING_VERSION_METHODS and methods
        if all_rolling:
            drift.append(record)
        else:
            disagreements.append(record)
    return disagreements, drift


def aggregate(
    input_dir: str | Path,
    kg_name: str,
    kg_version: str,
    packages: dict | None = None,
    artifacts: list[dict] | None = None,
) -> dict:
    """Read per-ingest metadata files and emit the consolidated build receipt.

    Returned shape: a top-level `Release` with `id=kg_name`, `version=kg_version`,
    nested `sources` (one per ingest, with their own leaves), plus `packages`
    (legacy compatibility key for `tools`) and `disagreements` (computed across
    the contributing builds).
    """
    per_ingest_docs = load_per_ingest_metadata(input_dir)
    nested_sources = [to_nested_release(d) for d in per_ingest_docs]
    disagreements, drift = find_disagreements(per_ingest_docs)

    receipt: dict = {
        "id": kg_name,
        "version": kg_version,
        "generated_at": _now_iso(),
    }
    if packages:
        receipt["packages"] = dict(packages)
    if artifacts:
        receipt["artifacts"] = list(artifacts)
    receipt["sources"] = nested_sources
    receipt["disagreements"] = disagreements
    receipt["version_drift"] = drift
    return receipt


def collect_kg_artifacts(output_dir: str | Path, names: list[str]) -> list[dict]:
    """Build a list of `{path, sha256}` for the named files in output_dir."""
    out_path = Path(output_dir)
    artifacts = []
    for name in names:
        p = out_path / name
        if not p.is_file():
            continue
        artifacts.append({"path": name, "sha256": _file_sha256(p)})
    return artifacts


def write_receipt(receipt: dict, output_path: str | Path) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(yaml.safe_dump(receipt, sort_keys=False, default_flow_style=False))
