"""Build dismech.duckdb: one pinned dismech release, flattened, plus the KG slices the API joins to.

The API attaches the output READ_ONLY and never touches monarch-kg.duckdb, so workers start
in milliseconds. dismech stays out of the KG: nothing here is written into KG nodes/edges.

Schemas:
  core  dismech's own content, no KG joins
          release              the dismech release this file was built from
          disorder             one row per disorder file
          node                 mechanism and phenotype nodes, for hover details
          causal_edge          downstream / sequelae edges between nodes
          phenotype            one row per (disorder, phenotype), with its upstream causal subgraph
          phenotype_mechanism  (mechanism node, phenotype) for every node upstream of a phenotype
          treatment            one row per (disorder, treatment), with agents and targets
          descriptor           ontology terms (GO, CL, UBERON, CHEBI, HGNC...) on mechanism nodes
          pathograph_disorder  dismech's pathograph index (MONDO -> graph file)
          pathograph_node      pathograph nodes as dismech renders them, per graph file
          pathograph_edge      pathograph edges, per graph file
          pathograph_gene      HGNC -> MONDO, from dismech's by_gene index
  app   shaped for monarch-app endpoints; may copy KG data
          kg_disease_phenotype KG disease -> phenotype edges, sorted by disease
          kg_phenotype_disease the same edges, sorted by phenotype
          hp_closure           HP subClassOf closure (reflexive)
          kg_node              labels for the CHEBI/GO/CL/UBERON/HGNC ids dismech uses, when the KG has them

Node ids are dismech:<file stem>#<slug of node name>. They are not stable across renames.

Inputs are dismech release assets (kb.zip, pathographs.zip, release_manifest.json), fetched by
`ingest download --ingests dismech`; kb and pathographs also take a directory (a dismech checkout,
or an unzipped pathographs/). Run as `ingest dismech-db`, after `prepare-solr`.
"""

import json
import os
import re
import tempfile
import zipfile
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path

import yaml

from monarch_ingest.cli_utils import connect_duckdb
from monarch_ingest.utils.log_utils import get_logger

logger = get_logger(__name__)

FREQ_HP = {
    "OBLIGATE": "HP:0040280",
    "VERY_FREQUENT": "HP:0040281",
    "FREQUENT": "HP:0040282",
    "OCCASIONAL": "HP:0040283",
    "VERY_RARE": "HP:0040284",
    "EXCLUDED": "HP:0040285",
}
DESCRIPTOR_SLOTS = [
    "gene",
    "genes",
    "cell_types",
    "biological_processes",
    "molecular_functions",
    "cellular_components",
    "locations",
    "chemical_entities",
]


def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")


def curie(value):
    """uppercase the prefix only (dismech writes hgnc:870, the KG HGNC:870)"""
    prefix, sep, local = (value or "").partition(":")
    return f"{prefix.upper()}:{local}" if sep else value or None


def term(d):
    t = (d or {}).get("term") or {}
    return curie(t.get("id")), t.get("label") or (d or {}).get("preferred_term")


def evidence(items):
    out = []
    for e in items or []:
        if isinstance(e, dict) and e.get("reference"):
            out.append(
                {
                    "reference": str(e["reference"]),
                    "title": e.get("reference_title"),
                    "supports": e.get("supports"),
                    "source": e.get("evidence_source"),
                    "snippet": (e.get("snippet") or "").strip() or None,
                }
            )
    return out


def descriptors(node):
    out = []
    for slot in DESCRIPTOR_SLOTS:
        v = node.get(slot)
        for d in v if isinstance(v, list) else [v] if v else []:
            if isinstance(d, dict):
                tid, label = term(d)
                if tid:
                    out.append({"slot": slot, "id": tid, "label": label, "modifier": d.get("modifier")})
    return out


def text(v):
    return (v or "").strip() or None if isinstance(v, str) else None


def enum(v):
    return str(v) if v else None


def read_disorders(kb):
    """(file stem, parsed yaml) for every disorder in a kb.zip or a dismech checkout"""
    if zipfile.is_zipfile(kb):
        with zipfile.ZipFile(kb) as z:
            for name in sorted(z.namelist()):
                if re.fullmatch(r"kb/disorders/[^/]+\.yaml", name) and not name.endswith(".history.yaml"):
                    yield Path(name).stem, yaml.load(z.read(name), Loader=yaml.CSafeLoader) or {}
    else:
        for f in sorted(Path(kb, "kb/disorders").glob("*.yaml")):
            if not f.name.endswith(".history.yaml"):
                yield f.stem, yaml.load(f.read_text(), Loader=yaml.CSafeLoader) or {}


def read_pathographs(src):
    """(file name, parsed json) for index.json, by_gene.json and every graph file"""
    if zipfile.is_zipfile(src):
        with zipfile.ZipFile(src) as z:
            for name in sorted(z.namelist()):
                if name.endswith(".json"):
                    yield Path(name).name, json.loads(z.read(name))
    else:
        for f in sorted(Path(src).glob("*.json")):
            yield f.name, json.loads(f.read_text())


def flatten(kb):
    tables = defaultdict(list)
    for stem, d in read_disorders(kb):
        mondo, _ = term(d.get("disease_term"))
        disorder = d.get("name")
        pathos = [p for p in d.get("pathophysiology") or [] if isinstance(p, dict) and p.get("name")]
        phens = [p for p in d.get("phenotypes") or [] if isinstance(p, dict) and p.get("name")]
        mechanisms = {p["name"] for p in pathos}
        hpo_by_name = {p["name"]: term(p.get("phenotype_term"))[0] for p in phens}

        def nid(name):
            return f"dismech:{stem}#{slug(name)}"

        base = {"disorder_file": stem, "mondo_id": mondo}
        tables["disorder"].append({**base, "name": disorder, "description": text(d.get("description"))})

        # target name -> [(source name, causal link type)]
        parents = defaultdict(list)
        for kind, items in (("downstream", pathos), ("sequelae", phens)):
            for src in items:
                for e in src.get(kind) or []:
                    if isinstance(e, dict) and e.get("target"):
                        parents[e["target"]].append((src["name"], e.get("causal_link_type")))
                        tables["causal_edge"].append(
                            {
                                **base,
                                "kind": kind,
                                "source_id": nid(src["name"]),
                                "target_id": nid(e["target"]),
                                "target_resolved": e["target"] in mechanisms or e["target"] in hpo_by_name,
                                "causal_link_type": e.get("causal_link_type"),
                                "hypothesis_groups": e.get("hypothesis_groups") or [],
                                "evidence": evidence(e.get("evidence")),
                            }
                        )

        for p in pathos:
            ds = descriptors(p)
            tables["node"].append(
                {
                    **base,
                    "node_id": nid(p["name"]),
                    "kind": "mechanism",
                    "name": p["name"],
                    "term_id": None,
                    "biological_scale": p.get("biological_scale"),
                    "description": text(p.get("description")),
                    "frequency": None,
                    "descriptors": ds,
                    "evidence": evidence(p.get("evidence")),
                }
            )
            for x in ds:
                tables["descriptor"].append(
                    {
                        **base,
                        "disorder": disorder,
                        "node_id": nid(p["name"]),
                        "node_name": p["name"],
                        "slot": x["slot"],
                        "term_id": x["id"],
                        "term_label": x["label"],
                        "modifier": x["modifier"],
                    }
                )
        for p in phens:
            hp, _ = term(p.get("phenotype_term"))
            tables["node"].append(
                {
                    **base,
                    "node_id": nid(p["name"]),
                    "kind": "phenotype",
                    "name": p["name"],
                    "term_id": hp,
                    "biological_scale": None,
                    "description": text(p.get("description")) or text(p.get("notes")),
                    "frequency": enum(p.get("frequency")),
                    "descriptors": [],
                    "evidence": evidence(p.get("evidence")),
                }
            )

        def upstream(name):
            """edges among every ancestor of `name`, plus the nearest mechanism ancestors"""
            seen, queue, edges, nearest = {name}, deque([name]), [], set()
            while queue:
                cur = queue.popleft()
                for src, link in parents.get(cur, []):
                    edges.append({"source": nid(src), "target": nid(cur), "link_type": link})
                    if src in mechanisms and cur not in mechanisms:
                        nearest.add(src)
                    if src not in seen:
                        seen.add(src)
                        queue.append(src)
            if not seen & mechanisms:
                return [], []
            unique = {(e["source"], e["target"]): e for e in edges}
            return list(unique.values()), sorted(nearest)

        for p in phens:
            hp, hp_label = term(p.get("phenotype_term"))
            onset_id, _ = term((p.get("phenotype_term") or {}).get("onset"))
            freq = p.get("frequency")
            edges, nearest = upstream(p["name"])
            tables["phenotype"].append(
                {
                    **base,
                    "disorder": disorder,
                    "phenotype_name": p["name"],
                    "phenotype_node_id": nid(p["name"]),
                    "hpo_id": hp,
                    "hpo_label": hp_label,
                    "frequency_hp": FREQ_HP.get(freq),
                    "frequency_text": None if freq in FREQ_HP else enum(freq),
                    "onset_hp": onset_id,
                    "severity": enum(p.get("severity")),
                    "diagnostic": bool(p.get("diagnostic")),
                    "evidence": evidence(p.get("evidence")),
                    "contexts": [
                        {
                            "population": c.get("population"),
                            "sex": enum(c.get("sex")),
                            "subtype": c.get("subtype"),
                            "frequency": enum(c.get("frequency")),
                        }
                        for c in p.get("phenotype_contexts") or []
                        if isinstance(c, dict)
                    ],
                    "nearest_mechanisms": nearest,
                    "upstream_edges": edges,
                }
            )

        for t in d.get("treatments") or []:
            if not isinstance(t, dict) or not t.get("name"):
                continue
            tt = t.get("treatment_term") or {}
            tid, tlabel = term(tt)
            agents = [
                {"id": a_id, "label": a_label}
                for a_id, a_label in (term(a) for a in tt.get("therapeutic_agent") or [] if isinstance(a, dict))
                if a_id
            ]
            tables["treatment"].append(
                {
                    **base,
                    "disorder": disorder,
                    "treatment_node_id": nid(t["name"]),
                    "name": t["name"],
                    "description": text(t.get("description")),
                    "modality": enum(t.get("therapeutic_modality")),
                    "action_category": enum(t.get("action_category")),
                    "treatment_term_id": tid,
                    "treatment_term_label": tlabel,
                    "agents": agents,
                    "target_mechanisms": [
                        {
                            "node_id": nid(m["target"]),
                            "name": m["target"],
                            "resolved": m["target"] in mechanisms,
                            "effect": enum(m.get("treatment_effect")),
                            "description": text(m.get("description")),
                            "evidence": evidence(m.get("evidence")),
                        }
                        for m in t.get("target_mechanisms") or []
                        if isinstance(m, dict) and m.get("target")
                    ],
                    "target_phenotypes": [
                        {"hpo_id": p_id, "label": p_label}
                        for p_id, p_label in (term(p) for p in t.get("target_phenotypes") or [] if isinstance(p, dict))
                        if p_id
                    ],
                    "evidence": evidence(t.get("evidence")),
                }
            )
    return tables


def pathograph_tables(src):
    tables = defaultdict(list)
    for name, data in read_pathographs(src):
        if name == "index.json":
            for mondo, entries in data.items():
                for e in entries:
                    tables["pathograph_disorder"].append(
                        {"mondo_id": curie(mondo), "file": e["file"], "name": e.get("name"), "slug": e.get("slug")}
                    )
        elif name == "by_gene.json":
            for gene, mondos in data.items():
                for mondo in mondos:
                    tables["pathograph_gene"].append({"gene_id": curie(gene), "mondo_id": curie(mondo)})
        else:
            for i, n in enumerate(data.get("nodes", [])):
                tables["pathograph_node"].append(
                    {
                        "file": name,
                        "ord": i,
                        "id": n["id"],
                        "node_type": n.get("node_type"),
                        "color": n.get("color"),
                        "is_orphan": bool(n.get("is_orphan")),
                        "description": n.get("description"),
                        "meta": json.dumps(n.get("meta")),
                    }
                )
            for i, e in enumerate(data.get("edges", [])):
                tables["pathograph_edge"].append(
                    {
                        "file": name,
                        "ord": i,
                        "source": e["source"],
                        "target": e["target"],
                        "predicate": e.get("predicate"),
                        "description": e.get("description"),
                    }
                )
    return tables


# sort keys are the numeric local id: DuckDB keeps only an 8-byte prefix of string min/max stats,
# and every MONDO/HP id shares "MONDO:00"/"HP:00000", so sorting on the string skips no row groups
_ID_KEY = "try_cast(split_part({col}, ':', 2) AS BIGINT)"


# per-entity lookups the API filters on, so reads skip most row groups
ORDER = {
    "phenotype": _ID_KEY.format(col="mondo_id") + ", mondo_id",
    "treatment": _ID_KEY.format(col="mondo_id") + ", mondo_id",
    "pathograph_disorder": _ID_KEY.format(col="mondo_id") + ", mondo_id",
    "pathograph_node": "file, ord",
    "pathograph_edge": "file, ord",
    "node": "node_id",
    "descriptor": "term_id",
}


def load(con, schema, tables, tmp):
    for name, rows in tables.items():
        path = Path(tmp, f"{schema}.{name}.jsonl")
        with open(path, "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        con.execute(
            f"CREATE TABLE {schema}.{name} AS SELECT * FROM read_json(?, format='newline_delimited', "
            f"sample_size=-1) ORDER BY {ORDER.get(name, 'ALL')}",
            [str(path)],
        )
        logger.info(f"{schema}.{name}: {len(rows)} rows")


def release_tag(manifest) -> str:
    """the dismech release tag recorded in a release's release_manifest.json"""
    return json.loads(Path(manifest).read_text())["release_tag"]


def build_dismech_db(kb, pathographs, kg, out, release: str):
    """write dismech.duckdb from a dismech release's kb and pathographs plus the merged KG"""
    out = Path(out)
    partial = out.with_suffix(".partial")
    partial.unlink(missing_ok=True)
    con = connect_duckdb(partial)
    con.execute("CREATE SCHEMA core")
    con.execute("CREATE SCHEMA app")
    with tempfile.TemporaryDirectory() as tmp:
        load(con, "core", flatten(kb), tmp)
        load(con, "core", pathograph_tables(pathographs), tmp)
    con.execute(
        "CREATE TABLE core.release AS SELECT ? AS release, ? AS kb, ? AS pathographs, ? AS built_at",
        [
            release,
            os.path.basename(kb),
            os.path.basename(pathographs),
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
        ],
    )
    # every mechanism node upstream of each phenotype, for "leads to" lookups by node
    con.execute(
        "CREATE TABLE core.phenotype_mechanism AS SELECT DISTINCT * FROM ("
        "  SELECT unnest(list_transform(upstream_edges, e -> e.source)) AS node_id, phenotype_node_id, mondo_id,"
        "    hpo_id, hpo_label, diagnostic FROM core.phenotype"
        ") ORDER BY node_id"
    )

    kg = str(Path(kg).resolve()).replace("'", "''")
    con.execute(f"ATTACH '{kg}' AS kg (READ_ONLY)")
    columns = (
        "subject, subject_label, object, object_label, negated, primary_knowledge_source, original_subject, "
        "frequency_qualifier, frequency_qualifier_label, has_percentage, has_count, has_total, "
        "onset_qualifier_label, sex_qualifier_label, publications, has_evidence"
    )
    source = (
        f"SELECT {_ID_KEY.format(col='subject')} AS subject_key, {_ID_KEY.format(col='object')} AS object_key, "
        f"{columns} FROM kg._solr_edges "
        "WHERE predicate = 'biolink:has_phenotype' AND subject LIKE 'MONDO:%'"
    )
    con.execute(f"CREATE TABLE app.kg_disease_phenotype AS {source} ORDER BY subject_key, subject")
    con.execute(f"CREATE TABLE app.kg_phenotype_disease AS {source} ORDER BY object_key, object")
    con.execute(
        "CREATE TABLE app.hp_closure AS "
        f"SELECT {_ID_KEY.format(col='object_id')} AS ancestor_key, subject_id AS hpo_id, object_id AS ancestor_id "
        "FROM kg.closure WHERE predicate_id = 'rdfs:subClassOf' "
        "AND subject_id LIKE 'HP:%' AND object_id LIKE 'HP:%' "
        "ORDER BY ancestor_key, hpo_id"
    )
    con.execute(
        "CREATE TABLE app.kg_node AS SELECT id, name, category FROM kg.nodes WHERE id IN ("
        "  SELECT term_id FROM core.descriptor"
        "  UNION SELECT unnest(agents).id FROM core.treatment"
        "  UNION SELECT gene_id FROM core.pathograph_gene"
        ") ORDER BY id"
    )
    for table in ("kg_disease_phenotype", "kg_phenotype_disease", "hp_closure", "kg_node"):
        logger.info(f"app.{table}: {con.execute(f'SELECT count(*) FROM app.{table}').fetchone()[0]} rows")
    con.execute("DETACH kg")
    con.execute("CHECKPOINT")
    con.close()
    # readers hold a lock on the old file; publish under the final name only when complete
    partial.replace(out)
    logger.info(f"wrote {out} ({out.stat().st_size / 1e6:.0f} MB) from dismech {release}")
