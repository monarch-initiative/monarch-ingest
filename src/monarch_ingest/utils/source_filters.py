"""Filters applied to downloaded KGX files before they reach the merge.

A `url:` / `repo:` ingest entry can name one of these with `filter: <name>`. The
raw downloads then land in `data/<ingest>/`, and the filter writes what the
merge should see to `<output_dir>/transform_output/`.
"""

import json
from collections import Counter
from pathlib import Path
from typing import Optional

from monarch_ingest.utils.log_utils import get_logger

# MeDIC drug nodes on these prefixes have no ontology source in the KG. Every
# other MeDIC node (CHEBI, MONDO, HP, UMLS) is either provided by phenio or has
# no ontology home, so edges to it are left to dangle and get reported.
MEDIC_NODE_PREFIXES = ("DRON:", "RXCUI:", "UNII:")
MEDIC_CONTEXT_PREFIX = "MONDO:"
# The drug-disease-compare label audit of this export found HIGH pairs wrong 7.9% of
# the time against 66.7% for LOW (and 18% for an undersampled MEDIUM).
MEDIC_RELIABILITY = "HIGH"
# Records from these jurisdictions are withheld from the KG, keyed to the authority
# MeDIC names for each. Edges carry the jurisdiction (upper case); drug nodes list
# approving jurisdictions and authorities in separate, unaligned lists, and their
# registration numbers are prefixed with the authority.
MEDIC_WITHHELD_JURISDICTIONS = {"india": "CDSCO", "russia": "MOH_RUSSIA", "china": "NMPA_CHINA"}
MEDIC_WITHHELD_AUTHORITIES = set(MEDIC_WITHHELD_JURISDICTIONS.values())


def _medic_exclusion(edge: dict) -> Optional[str]:
    """Why an edge is excluded, or None to keep it: it must not come from a withheld
    jurisdiction, its (drug, condition) pair must be HIGH reliability, and its disease
    context empty or a MONDO term (not free text or UMLS)."""
    if (edge.get("medic_jurisdiction") or "").lower() in MEDIC_WITHHELD_JURISDICTIONS:
        return "withheld jurisdiction"
    if edge.get("medic_pair_reliability") != MEDIC_RELIABILITY:
        return "pair reliability not HIGH"
    context = edge.get("disease_context_qualifier")
    if context is not None and not context.startswith(MEDIC_CONTEXT_PREFIX):
        return "non-MONDO disease context"
    return None


def _withhold_node_approvals(node: dict) -> bool:
    """Drop withheld jurisdictions' entries from a drug node's approval lists, in
    place. Returns whether anything was dropped."""
    keeps = {
        "medic_approved_jurisdictions": lambda v: v not in MEDIC_WITHHELD_JURISDICTIONS,
        "medic_approved_authorities": lambda v: v not in MEDIC_WITHHELD_AUTHORITIES,
        "medic_registration_numbers": lambda v: v.split(":", 1)[0] not in MEDIC_WITHHELD_AUTHORITIES,
    }
    changed = False
    for field, keep in keeps.items():
        values = node.get(field)
        if not values:
            continue
        kept = [v for v in values if keep(v)]
        if len(kept) != len(values):
            changed = True
            if kept:
                node[field] = kept
            else:
                del node[field]
    return changed


def filter_medic(raw_dir: Path, output_dir: Path, qc_dir: Path) -> None:
    """Load MeDIC's edges, and only the drug nodes phenio can't provide.

    Excluded edges are written to `qc_dir/medic_excluded_edges.jsonl`. Lines are
    copied through unchanged, except drug nodes that list a withheld jurisdiction's
    approvals, which are rewritten without them.
    """
    logger = get_logger(None)
    output_dir.mkdir(parents=True, exist_ok=True)
    qc_dir.mkdir(parents=True, exist_ok=True)

    subjects = set()
    kept = 0
    excluded = Counter()
    with (
        open(raw_dir / "medic_edges.jsonl") as src,
        open(output_dir / "medic_edges.jsonl", "w") as out,
        open(qc_dir / "medic_excluded_edges.jsonl", "w") as rejected,
    ):
        for line in src:
            if not line.strip():
                continue
            edge = json.loads(line)
            reason = _medic_exclusion(edge)
            if reason is None:
                out.write(line)
                subjects.add(edge["subject"])
                kept += 1
            else:
                rejected.write(line)
                excluded[reason] += 1
    logger.info(
        f"medic: kept {kept} edges, excluded "
        + ", ".join(f"{n} ({reason})" for reason, n in excluded.most_common())
    )

    nodes = 0
    stripped = 0
    with open(raw_dir / "medic_nodes.jsonl") as src, open(output_dir / "medic_nodes.jsonl", "w") as out:
        for line in src:
            if not line.strip():
                continue
            node = json.loads(line)
            node_id = node["id"]
            if node_id.startswith(MEDIC_NODE_PREFIXES) and node_id in subjects:
                if _withhold_node_approvals(node):
                    line = json.dumps(node, ensure_ascii=False) + "\n"
                    stripped += 1
                out.write(line)
                nodes += 1
    logger.info(
        f"medic: kept {nodes} drug nodes on {', '.join(MEDIC_NODE_PREFIXES)}, "
        f"{stripped} with withheld jurisdictions' approvals removed"
    )


SOURCE_FILTERS = {
    "medic": filter_medic,
}
