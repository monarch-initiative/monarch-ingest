"""Render a human-readable `release-notes.md` from the build receipt + QC report.

The build receipt (`release_metadata.aggregate`) and `qc_report.yaml` are
machine-readable snapshots; this module turns them into prose that answers
*what changed since the last release*:

- graph size deltas (nodes/edges) from the QC summary,
- source version changes, added/removed sources, walked out of the receipt's
  (recursively nested) `sources`,
- per-provider node/edge count deltas from the QC report,
- any free-text notes an ingest published in its `release-metadata.yaml`,
- the cross-ingest `disagreements` / `version_drift` already on the receipt.

Rolling sources (timestamp-based `version_method`, e.g. an advancing
Last-Modified header) are separated from stable, tagged sources so routine
re-pulls don't drown out real version bumps. See `find_disagreements` in
`release_metadata` for the same rolling/stable split applied to conflicts.
"""

from __future__ import annotations

from pathlib import Path

import requests
import yaml

from monarch_ingest.release_metadata import ROLLING_VERSION_METHODS

# Diff against the previous *production* (non-draft) release, not the daily
# monarch-kg-dev builds — consecutive dev rebuilds differ by almost nothing, so
# the meaningful changelog lives between the spaced-out monarch-kg releases.
DEFAULT_PREVIOUS_BASE_URL = "https://data.monarchinitiative.org/monarch-kg/latest/"


def _iter_sources(nodes):
    """Depth-first walk over a receipt's nested `sources` lists."""
    for node in nodes or []:
        yield node
        yield from _iter_sources(node.get("sources"))


def flatten_sources(receipt: dict) -> dict[str, dict]:
    """Collapse the receipt's nested `sources` to `{infores_id: {...}}`.

    The receipt nests ingest Releases, each carrying their own `sources`, which
    may nest further (kg-phenio -> phenio -> upstream ontologies). We collect
    every `infores:`-prefixed leaf regardless of depth. The first observation of
    an id wins; cross-ingest version conflicts are surfaced separately by
    `release_metadata.find_disagreements`, so we don't re-litigate them here.
    """
    flat: dict[str, dict] = {}
    for node in _iter_sources(receipt.get("sources")):
        sid = node.get("id")
        if sid and sid.startswith("infores:") and sid not in flat:
            flat[sid] = {
                "version": node.get("version"),
                "version_method": node.get("version_method"),
            }
    return flat


def diff_sources(current: dict[str, dict], previous: dict[str, dict]) -> dict:
    """Compare two `flatten_sources` maps into added/removed/changed buckets."""
    cur_ids, prev_ids = set(current), set(previous)
    changed = []
    for sid in sorted(cur_ids & prev_ids):
        if current[sid]["version"] != previous[sid]["version"]:
            method = current[sid].get("version_method")
            changed.append(
                {
                    "id": sid,
                    "from": previous[sid]["version"],
                    "to": current[sid]["version"],
                    "version_method": method,
                    "rolling": method in ROLLING_VERSION_METHODS,
                }
            )
    return {
        "added": sorted(cur_ids - prev_ids),
        "removed": sorted(prev_ids - cur_ids),
        "changed": changed,
    }


def collect_ingest_notes(receipt: dict) -> list[dict]:
    """Gather free-text notes an ingest published, if any.

    An ingest may set a `notes` (or `changelog`) field in its
    `release-metadata.yaml`; we surface those verbatim. Ingests that don't set
    one simply don't appear here.
    """
    notes = []
    for ingest in receipt.get("sources") or []:
        text = ingest.get("notes") or ingest.get("changelog")
        if text:
            notes.append({"ingest": ingest.get("id"), "text": str(text).strip()})
    return notes


def _count_map(qc_report: dict | None, key: str) -> dict[str, int]:
    if not qc_report:
        return {}
    return {row["name"]: row.get("total_number", 0) for row in (qc_report.get(key) or []) if "name" in row}


def diff_counts(current_qc: dict | None, previous_qc: dict | None, key: str) -> list[dict]:
    """Per-provider count changes for `nodes` or `edges`, biggest move first."""
    cur, prev = _count_map(current_qc, key), _count_map(previous_qc, key)
    rows = []
    for name in sorted(set(cur) | set(prev)):
        c, p = cur.get(name), prev.get(name)
        if c == p:
            continue
        rows.append({"name": name, "from": p, "to": c, "delta": (c or 0) - (p or 0)})
    rows.sort(key=lambda r: abs(r["delta"]), reverse=True)
    return rows


def _fmt(n) -> str:
    return f"{n:,}" if isinstance(n, int) else "—" if n is None else str(n)


def _fmt_delta(n: int) -> str:
    return f"+{n:,}" if n > 0 else f"{n:,}"


def _summary_line(label: str, cur, prev) -> str:
    if isinstance(cur, int) and isinstance(prev, int) and cur != prev:
        return f"- {label}: {_fmt(cur)} ({_fmt_delta(cur - prev)})"
    return f"- {label}: {_fmt(cur)}"


def render_release_notes(
    receipt: dict,
    qc_report: dict | None = None,
    prev_receipt: dict | None = None,
    prev_qc_report: dict | None = None,
) -> str:
    """Render the release notes as a Markdown string."""
    lines: list[str] = []
    version = receipt.get("version", "unknown")
    kg = receipt.get("id", "monarch-kg")
    lines.append(f"# {kg} {version} — release notes")
    lines.append("")

    pkgs = receipt.get("packages") or {}
    pkg_str = " · ".join(f"{k} {v}" for k, v in pkgs.items())
    meta = f"_Generated {receipt.get('generated_at', '?')}"
    if pkg_str:
        meta += f" · {pkg_str}"
    meta += "._"
    lines.append(meta)
    if prev_receipt:
        lines.append(f"_Compared against {prev_receipt.get('id', kg)} {prev_receipt.get('version', '?')}._")
    else:
        lines.append("_No previous release available for comparison — showing current totals only._")
    lines.append("")

    # --- Graph size ---
    summary = (qc_report or {}).get("summary") or {}
    prev_summary = (prev_qc_report or {}).get("summary") or {}
    if summary:
        lines.append("## Graph size")
        for label, field in (
            ("Nodes", "total_nodes"),
            ("Edges", "total_edges"),
            ("Dangling edges", "dangling_edges"),
            ("Duplicate nodes", "duplicate_nodes"),
        ):
            if field in summary:
                lines.append(_summary_line(label, summary.get(field), prev_summary.get(field)))
        lines.append("")

    # --- Source version changes ---
    cur_sources = flatten_sources(receipt)
    if prev_receipt is not None:
        d = diff_sources(cur_sources, flatten_sources(prev_receipt))
        stable = [c for c in d["changed"] if not c["rolling"]]
        rolling = [c for c in d["changed"] if c["rolling"]]

        lines.append("## Source version changes")
        if stable:
            lines.append("")
            lines.append("### Stable sources")
            for c in stable:
                lines.append(f"- `{c['id']}`: {_fmt(c['from'])} → {_fmt(c['to'])}")
        if rolling:
            lines.append("")
            lines.append("### Rolling re-pulls")
            for c in rolling:
                lines.append(f"- `{c['id']}`: {_fmt(c['from'])} → {_fmt(c['to'])} ({c['version_method']})")
        if not stable and not rolling:
            lines.append("")
            lines.append("_No source version changes._")
        lines.append("")

        if d["added"]:
            lines.append("## Sources added")
            for sid in d["added"]:
                lines.append(f"- `{sid}` ({_fmt(cur_sources[sid]['version'])})")
            lines.append("")
        if d["removed"]:
            lines.append("## Sources removed")
            for sid in d["removed"]:
                lines.append(f"- `{sid}`")
            lines.append("")
    elif cur_sources:
        lines.append("## Sources")
        for sid in sorted(cur_sources):
            lines.append(f"- `{sid}` ({_fmt(cur_sources[sid]['version'])})")
        lines.append("")

    # --- Per-provider count changes (only when we have something to diff against) ---
    if prev_qc_report is not None and qc_report is not None:
        for key, heading in (("nodes", "node"), ("edges", "edge")):
            rows = diff_counts(qc_report, prev_qc_report, key)
            if not rows:
                continue
            lines.append(f"## Per-provider {heading} count changes")
            lines.append("")
            lines.append(f"| provider | before | after | Δ |")
            lines.append("| --- | ---: | ---: | ---: |")
            for r in rows:
                lines.append(f"| {r['name']} | {_fmt(r['from'])} | {_fmt(r['to'])} | {_fmt_delta(r['delta'])} |")
            lines.append("")

    # --- Notes gathered from individual ingests ---
    notes = collect_ingest_notes(receipt)
    if notes:
        lines.append("## Notes from ingests")
        for n in notes:
            lines.append("")
            lines.append(f"### {n['ingest']}")
            lines.append(n["text"])
        lines.append("")

    # --- Flags already computed on the receipt ---
    disagreements = receipt.get("disagreements") or []
    drift = receipt.get("version_drift") or []
    if disagreements or drift:
        lines.append("## Flags")
        if disagreements:
            lines.append("")
            lines.append("### Version disagreements")
            lines.append("_Same source consumed at different versions across ingests (at least one tagged)._")
            for d in disagreements:
                lines.append(f"- `{d['id']}`: {d.get('by_ingest')}")
        if drift:
            lines.append("")
            lines.append("### Rolling-source drift")
            lines.append("_Rolling sources re-pulled at different snapshots across ingests (expected)._")
            for d in drift:
                lines.append(f"- `{d['id']}`: {d.get('by_ingest')}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def load_previous_release(
    base_url: str | None = None,
    previous_dir: str | Path | None = None,
    kg_name: str = "monarch-kg",
) -> tuple[dict | None, dict | None]:
    """Best-effort fetch of the previous release's receipt + QC report.

    Reads from `previous_dir` when given (local path), otherwise from
    `base_url` (defaults to the published `latest/`). Any failure — network
    error, 404, unparseable YAML — returns `None` for that document so the
    renderer falls back to a first-release layout instead of crashing the build.
    """

    def _load(name: str) -> dict | None:
        try:
            if previous_dir is not None:
                p = Path(previous_dir) / name
                return yaml.safe_load(p.read_text()) if p.is_file() else None
            url = (base_url or DEFAULT_PREVIOUS_BASE_URL).rstrip("/") + "/" + name
            resp = requests.get(url, allow_redirects=True, timeout=30)
            return yaml.safe_load(resp.content) if resp.ok else None
        except (requests.RequestException, yaml.YAMLError, OSError):
            return None

    return _load("metadata.yaml"), _load("qc_report.yaml")


def write_release_notes(markdown: str, output_path: str | Path) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(markdown)
