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
# Regulators whose content is left out of the KG: their edges (by
# medic_jurisdiction) and their mentions in drug-node properties. In v2.0.0
# only India has edges; China and Russia appear only on nodes.
MEDIC_EXCLUDED_JURISDICTIONS = {"CHINA", "INDIA", "RUSSIA"}
MEDIC_EXCLUDED_AUTHORITIES = {"NMPA_CHINA", "CDSCO", "MOH_RUSSIA"}


def _medic_exclusion(edge: dict) -> Optional[str]:
    """Why an edge is excluded, or None to keep it: its (drug, condition) pair must be
    HIGH reliability, it must not come from an excluded jurisdiction, and its disease
    context must be empty or a MONDO term (not free text or UMLS)."""
    if edge.get("medic_pair_reliability") != MEDIC_RELIABILITY:
        return "pair reliability not HIGH"
    if str(edge.get("medic_jurisdiction") or "").upper() in MEDIC_EXCLUDED_JURISDICTIONS:
        return "excluded jurisdiction"
    context = edge.get("disease_context_qualifier")
    if context is not None and not context.startswith(MEDIC_CONTEXT_PREFIX):
        return "non-MONDO disease context"
    return None


def _strip_excluded_jurisdictions(node: dict) -> bool:
    """Remove excluded regulators from a drug node's approval properties, in place.
    Returns whether anything changed."""
    changed = False
    for field, keep in (
        ("medic_approved_jurisdictions", lambda v: v.upper() not in MEDIC_EXCLUDED_JURISDICTIONS),
        ("medic_approved_authorities", lambda v: v.upper() not in MEDIC_EXCLUDED_AUTHORITIES),
        ("medic_registration_numbers", lambda v: v.split(":", 1)[0].upper() not in MEDIC_EXCLUDED_AUTHORITIES),
    ):
        values = node.get(field)
        if not isinstance(values, list):
            continue
        kept = [v for v in values if keep(str(v))]
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
    copied through unchanged, except kept drug nodes that mention an excluded
    jurisdiction, which are rewritten without it.
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

    nodes = stripped = 0
    with open(raw_dir / "medic_nodes.jsonl") as src, open(output_dir / "medic_nodes.jsonl", "w") as out:
        for line in src:
            if not line.strip():
                continue
            node = json.loads(line)
            if node["id"].startswith(MEDIC_NODE_PREFIXES) and node["id"] in subjects:
                if _strip_excluded_jurisdictions(node):
                    line = json.dumps(node, ensure_ascii=False) + "\n"
                    stripped += 1
                out.write(line)
                nodes += 1
    logger.info(
        f"medic: kept {nodes} drug nodes on {', '.join(MEDIC_NODE_PREFIXES)}"
        f" ({stripped} with excluded jurisdictions removed from their properties)"
    )


SOURCE_FILTERS = {
    "medic": filter_medic,
}
