"""BDC KG coverage report — Monarch KG edges across a fixed set of rubric type-pairs.

One-off (probably) — not wired into the merge/QC pipeline.

Reads `denormalized_edges` directly from `output/monarch-kg.duckdb` so we can
include `original_predicate` in the grouping — the canonical
`edge_report.parquet` materialization doesn't carry it, and we want it for
the `related_to` carve-out (below). Rolls up to one row per
(Subject Type, display predicate, Object Type), where:

  * Subject/Object "Node Type" is the rubric label (Disease, Phenotype,
    Gene / Variant, Body Part, Drug, Procedure, Measurement / Clinical Lab,
    Imaging / Waveform).
  * Subject/Object "Node Biolink Term" lists the actual biolink classes
    that contributed to the bucket in this row.
  * "Where does the annotation come from in the Monarch KG?" lists the
    distinct `primary_knowledge_source` values.
  * "# of edges in Monarch KG" sums the `count` column.

Filtering:
  * Each rubric type expands to its biolink class plus *all biolink
    descendants*, so future biolink-tagged nodes land automatically.
  * Each rubric pair is emitted in BOTH directions (Subject→Object and
    Object→Subject) as separate rows; same-type self-pairs appear once.
  * `(Gene|SequenceVariant)` ↔ `Genotype` edges (`has_sequence_variant`
    and the equivalent `related_to`) are part-of structural assertions
    and are dropped before aggregation.

`related_to` enrichment:
  * Phenio flattens specific RO terms (e.g. RO:0004003 "has material basis
    in germline mutation in") to `biolink:related_to` when the RO term
    has no 1:1 biolink slot. Without recording `original_predicate` they
    all collapse into a single uninformative `related_to` row.
  * Solution: keep a single `related_to` row per (subj_type, obj_type)
    pair, but in the Notes column list the distinct `original_predicate`
    values that contributed, each labeled from `phenio_nodes.tsv`
    (e.g. `RO:0004003 (has material basis in germline mutation in)`).
  * Only `related_to` is enriched this way; other predicates are
    biolink-canonical mappings, not lossy fall-throughs.

Output: TSV at `output/reports/bdc_kg_coverage.tsv`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import duckdb
from linkml_runtime.utils.formatutils import camelcase
from linkml_runtime.utils.schemaview import SchemaView


KG_DUCKDB = Path("output/monarch-kg.duckdb")
PHENIO_NODES = Path("output/transform_output/phenio_nodes.tsv")
OUTPUT_TSV = Path("output/reports/bdc_kg_coverage.tsv")

BIOLINK_VERSION = "4.4.2"

# Rubric labels → biolink class roots. Each root expands to itself + all
# descendants via SchemaView. None means "not represented in biolink as
# such" (carried through the report as 0 for completeness).
RUBRIC_ROOTS: dict[str, list[str | None]] = {
    "Disease": ["disease"],
    "Phenotype": ["phenotypic feature"],
    "Gene / Variant": ["gene", "sequence variant", "genotype"],
    "Body Part": ["anatomical entity"],  # cellular component is a descendant
    "Drug": ["chemical entity"],
    "Procedure": ["procedure"],
    "Measurement / Clinical Lab": ["clinical measurement", "clinical attribute"],
    "Imaging / Waveform": [None],
}

# Rubric pairs as listed in the original spec (Subject Type, Object Type).
# We emit each in BOTH directions; self-pairs appear once.
RUBRIC_PAIRS: list[tuple[str, str]] = [
    ("Disease", "Disease"),
    ("Disease", "Phenotype"),
    ("Disease", "Gene / Variant"),
    ("Disease", "Measurement / Clinical Lab"),
    ("Disease", "Drug"),
    ("Disease", "Body Part"),
    ("Disease", "Procedure"),
    ("Disease", "Imaging / Waveform"),
    ("Measurement / Clinical Lab", "Disease"),
    ("Measurement / Clinical Lab", "Phenotype"),
    ("Measurement / Clinical Lab", "Measurement / Clinical Lab"),
    ("Measurement / Clinical Lab", "Drug"),
    ("Measurement / Clinical Lab", "Body Part"),
    ("Body Part", "Body Part"),
    ("Body Part", "Disease"),
    ("Body Part", "Measurement / Clinical Lab"),
    ("Body Part", "Drug"),
    ("Body Part", "Procedure"),
]


def biolink_classes_for(roots: list[str | None], sv: SchemaView) -> set[str]:
    """Expand each root to itself + descendants, in `biolink:CamelCase` form."""
    out: set[str] = set()
    for r in roots:
        if r is None:
            continue
        # `class_descendants` returns the class + descendants by default.
        for c in sv.class_descendants(r):
            out.add(f"biolink:{camelcase(c)}")
    return out


def bidirectional_pairs(pairs: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Add reverse direction for each pair, deduped."""
    seen: set[tuple[str, str]] = set()
    out: list[tuple[str, str]] = []
    for a, b in pairs:
        for x, y in [(a, b), (b, a)]:
            if (x, y) not in seen:
                seen.add((x, y))
                out.append((x, y))
    return out


def load_id_to_label(nodes_tsv: Path) -> dict[str, str]:
    """Build a CURIE → label map from the transformed phenio nodes file.

    phenio_nodes.tsv carries 300+ RO predicate classes (plus the rest of
    the phenio ontology nodes) with their labels in the `name` column.
    We use it as the local source of truth for original_predicate labels
    in the Notes column, avoiding any extra network/dep.
    """
    if not nodes_tsv.exists():
        return {}
    labels: dict[str, str] = {}
    with nodes_tsv.open() as f:
        header = next(f).rstrip("\n").split("\t")
        id_col = header.index("id")
        name_col = header.index("name")
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) > max(id_col, name_col):
                cid = parts[id_col]
                name = parts[name_col]
                if cid and name and cid not in labels:
                    labels[cid] = name
    return labels


def main() -> int:
    if not KG_DUCKDB.exists():
        sys.exit(
            f"Missing {KG_DUCKDB}. Run `uv run ingest merge --closure` first "
            f"so denormalized_edges is materialized."
        )

    OUTPUT_TSV.parent.mkdir(parents=True, exist_ok=True)

    sv = SchemaView(
        f"https://raw.githubusercontent.com/biolink/biolink-model/v{BIOLINK_VERSION}/biolink-model.yaml"
    )
    rubric_classes = {label: biolink_classes_for(roots, sv) for label, roots in RUBRIC_ROOTS.items()}
    id_to_label = load_id_to_label(PHENIO_NODES)

    # Connect read-only to keep this safe to run alongside anything else
    # touching the duckdb (and to stay consistent with the parallel-readers
    # convention we landed in #689).
    con = duckdb.connect(str(KG_DUCKDB), read_only=True)
    # Use a single-shot CTE rather than a view since we're querying through
    # the duckdb's own denormalized_edges table.
    con.execute("CREATE TEMP VIEW e AS SELECT * FROM denormalized_edges")

    # Materialize the rubric-type → classes mapping as a temp table so we
    # can join in DuckDB rather than fanning through Python.
    con.execute("CREATE TEMP TABLE rubric (type TEXT, category TEXT)")
    for label, classes in rubric_classes.items():
        for cls in classes:
            con.execute("INSERT INTO rubric VALUES (?, ?)", [label, cls])

    # Apply the Genotype part-of drop universally — these are
    # `has_sequence_variant` and the equivalent `related_to` linking a
    # Genotype to its constituent Gene/SequenceVariant (~351k edges in
    # current KG). No biology lost.
    GENOTYPE_DROP_SQL = """
      NOT (
        (subject_category = 'biolink:Genotype'
         AND object_category IN ('biolink:Gene','biolink:SequenceVariant'))
        OR
        (object_category  = 'biolink:Genotype'
         AND subject_category IN ('biolink:Gene','biolink:SequenceVariant'))
      )
    """

    # Aggregate: one row per (subject rubric label, predicate, object
    # rubric label). For `related_to` rows we additionally collect the
    # distinct `original_predicate` values so the Notes column can list
    # the specific RO terms that flattened into it.
    rollup = con.execute(
        f"""
        WITH labeled AS (
          SELECT
            rs.type AS subj_type,
            ro.type AS obj_type,
            e.subject_category,
            e.object_category,
            e.predicate,
            e.original_predicate,
            e.primary_knowledge_source
          FROM e
          JOIN rubric rs ON rs.category = e.subject_category
          JOIN rubric ro ON ro.category = e.object_category
          WHERE {GENOTYPE_DROP_SQL}
        )
        SELECT
          subj_type,
          obj_type,
          predicate,
          list_sort(array_agg(DISTINCT subject_category))     AS subj_classes,
          list_sort(array_agg(DISTINCT object_category))      AS obj_classes,
          list_sort(
            array_agg(DISTINCT primary_knowledge_source)
              FILTER (WHERE primary_knowledge_source IS NOT NULL)
          )                                                   AS sources,
          list_sort(
            array_agg(DISTINCT original_predicate)
              FILTER (
                WHERE predicate = 'biolink:related_to'
                  AND original_predicate IS NOT NULL
                  AND original_predicate != ''
              )
          )                                                   AS original_predicates,
          count(*)                                            AS edges
        FROM labeled
        GROUP BY subj_type, obj_type, predicate
        """
    ).fetchall()

    rollup_index: dict[tuple[str, str], list[tuple]] = {}
    for row in rollup:
        rollup_index.setdefault((row[0], row[1]), []).append(row)

    cols = [
        "Subject Node Type",
        "Subject Node Biolink Term",
        "Relationship / Edge Type",
        "Object Node Type",
        "Object Node Biolink Term",
        "# of edges in Monarch KG",
        "Where does the annotation come from in the Monarch KG?",
        "Notes",
    ]

    # Strip the two prefixes that are universal in this report — `biolink:`
    # is implied by every category/predicate value, and `infores:` is implied
    # by every source. Easier to read without them.
    STRIP_PREFIXES = ("biolink:", "infores:")

    def strip(s: str) -> str:
        for p in STRIP_PREFIXES:
            if s.startswith(p):
                return s[len(p) :]
        return s

    def fmt(lst):
        if not lst:
            return ""
        return ", ".join(strip(v) for v in lst)

    def format_notes(original_predicates) -> str:
        """For a `related_to` row, list its RO/UPHENO/etc. original
        predicates with labels when we have them, falling back to bare
        CURIE for unknowns. Empty for non-`related_to` rows."""
        if not original_predicates:
            return ""
        parts = []
        for op in original_predicates:
            if not op:
                continue
            label = id_to_label.get(op)
            parts.append(f"{op} ({label})" if label else op)
        if not parts:
            return ""
        return "Flattened from: " + "; ".join(parts)

    with OUTPUT_TSV.open("w") as out:
        out.write("\t".join(cols) + "\n")
        for subj_type, obj_type in bidirectional_pairs(RUBRIC_PAIRS):
            rows = rollup_index.get((subj_type, obj_type), [])
            if not rows:
                # Emit one empty placeholder so the rubric is visible even
                # when the KG has no edges of this shape today (Procedure,
                # Measurement/Clinical Lab, Imaging/Waveform).
                # Use the configured biolink terms so the reader can see
                # the intended classes.
                out.write(
                    "\t".join(
                        [
                            subj_type,
                            fmt(sorted(rubric_classes[subj_type])),
                            "",
                            obj_type,
                            fmt(sorted(rubric_classes[obj_type])),
                            "0",
                            "",
                            "",
                        ]
                    )
                    + "\n"
                )
                continue
            # row shape: (subj_type, obj_type, predicate, subj_classes,
            #             obj_classes, sources, original_predicates, edges)
            for (
                _,
                _,
                predicate,
                subj_classes,
                obj_classes,
                sources,
                original_predicates,
                edges,
            ) in sorted(rows, key=lambda r: -int(r[7])):
                out.write(
                    "\t".join(
                        [
                            subj_type,
                            fmt(list(subj_classes)),
                            strip(predicate or ""),
                            obj_type,
                            fmt(list(obj_classes)),
                            str(int(edges)),
                            fmt(list(sources) if sources else []),
                            format_notes(list(original_predicates) if original_predicates else []),
                        ]
                    )
                    + "\n"
                )

    print(f"Wrote {OUTPUT_TSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
