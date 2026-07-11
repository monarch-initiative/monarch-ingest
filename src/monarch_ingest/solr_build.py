"""Runtime-agnostic Solr index builder.

The Apptainer/Docker-agnostic replacement for ``scripts/load_solr.sh``. Behaviour
is a faithful port of that script (same cores, schema steps, loads, verification,
tarball) with the three Docker-locked pieces abstracted behind :class:`SolrRuntime`:

  * **starting Solr** — ``docker run`` vs ``apptainer run`` (bind a host solr-home);
  * **creating cores** — the old flow used ``lsolr add-cores`` which shells out to
    ``docker exec``; here cores are created over the HTTP Cores API, which works
    identically under either runtime;
  * **tarring the index** — a Docker ``--volumes-from`` sidecar vs a plain ``tar``
    of the Apptainer host bind dir.

Single-core to start (entity / association / sssom / infores). The per-core load
is isolated in :func:`bulkload_core`, which is the seam a sharded loader
(hash-partition -> N cores -> MERGEINDEXES) drops into next.

Wire-up: ``ingest build-solr`` (see main.py). The legacy ``ingest solr`` /
``scripts/load_solr.sh`` path is left intact until this is validated end-to-end.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, ThreadPoolExecutor, as_completed, wait
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import duckdb
import requests
from requests.adapters import HTTPAdapter

from monarch_ingest.utils.log_utils import get_logger

logger = get_logger(__name__)

# Cores whose committed doc count must equal the distinct-id count of their source
# table. A silently short index is the worst release defect we can ship (build #328
# published a half-empty entity core that still passed), so these are asserted.
_VERIFY_SOURCE = {"entity": "denormalized_nodes", "association": "_solr_edges"}


@dataclass
class SolrBuildConfig:
    """Inputs and tunables for a Solr build (duckdb source, runtime, sizing, output)."""

    duckdb: Path = Path("output/monarch-kg.duckdb")
    schema: Path = Path("output/monarch-kg-schema.yaml")
    infores_yaml: Path = Path("data/infores/information_resource_registry.yaml")
    infores_jsonl: Path = Path("data/infores/infores_catalog.jsonl")

    # runtime: "docker" | "apptainer" | "" (auto: MONARCH_SOLR_RUNTIME, then docker, then apptainer)
    runtime: str = ""
    image: str = "solr:8"  # docker image ref, and the source apptainer pulls from
    sif: Optional[Path] = None  # apptainer .sif; pulled from `image` if missing
    container: str = "my_solr"  # docker container name
    solrhome: Path = Path(".solrhome")  # host dir bound to /var/solr under apptainer

    host: str = "localhost"
    port: int = 8983
    memory: str = "12g"  # container memory limit (docker -m)
    heap: str = "10g"  # JVM -Xms/-Xmx
    active_processors: Optional[int] = None  # -XX:ActiveProcessorCount; set on hosts where nproc/cgroup
    #   under-reports CPUs (SLURM cpuset), else Lucene's merge scheduler auto-throttles merge I/O to a crawl
    ram_buffer_mb: int = 2048
    parallel_workers: int = 4
    chunk_size: int = 100_000

    skip_tarball: bool = False  # SOLR_SKIP_TARBALL=1 equivalent
    tarball: Path = Path("output/solr.tar.gz")
    scripts_dir: Path = Path("scripts")
    dry_run: bool = False

    # -- sharded build (step 2): shard one big core N ways, load in parallel with
    #    our streaming loader, then MERGEINDEXES-collapse into `sharded_target`.
    n_shards: int = 1
    upload_workers: int = 4  # concurrent POST threads *within* each shard
    duckdb_memory_limit: str = "4GB"  # capped per shard reader so N readers stay bounded
    batch_size: int = 5000
    merge_threads: int = 2  # ConcurrentMergeScheduler maxThreadCount per shard (so N shards != 4N threads)
    merge_timeout: int = 7200  # seconds to wait for the MERGEINDEXES collapse to finish
    sharded_table: str = "_solr_edges"
    sharded_top_class: str = "Association"
    sharded_copyfields: str = "add_association_copyfields.sh"
    sharded_target: str = "association"

    # PreAnalyzedField: pre-tokenize the closure-label fields once per distinct value
    # (~356K) instead of re-analyzing every occurrence (~617M) at index time. Cuts
    # index-time analysis CPU; the _t fields are populated by the loader (not copyField).
    preanalyze_closure_labels: bool = False
    preanalyze_via_fieldtype: str = "text"  # analyzer to pre-run (must match the query analyzer)

    @property
    def preanalyze_map(self) -> tuple:
        """(raw duckdb column -> target *_t field) pairs to pre-analyze, or ()."""
        if not self.preanalyze_closure_labels:
            return ()
        # subject/object closure labels are the searched _t fields (see the association qf)
        return (
            ("subject_closure_label", "subject_closure_label_t"),
            ("object_closure_label", "object_closure_label_t"),
        )

    @property
    def base_url(self) -> str:
        """Base Solr URL, e.g. http://localhost:8983/solr."""
        return f"http://{self.host}:{self.port}/solr"


def detect_runtime(preference: str = "", *, check: bool = True) -> str:
    """Resolve the container runtime: explicit arg, env, then docker, then apptainer.

    ``check=False`` (used for dry runs) skips the PATH existence test so a plan
    can be printed on a host that lacks the target runtime.
    """
    choice = preference or os.environ.get("MONARCH_SOLR_RUNTIME", "")
    if choice:
        if check and not shutil.which(choice):
            raise RuntimeError(f"requested solr runtime '{choice}' is not on PATH")
        return choice
    for candidate in ("docker", "apptainer"):
        if shutil.which(candidate):
            return candidate
    if not check:
        return "docker"
    raise RuntimeError("no container runtime found — need `docker` or `apptainer` on PATH")


def _run(cmd: list[str], *, dry_run: bool, **kwargs) -> Optional[subprocess.CompletedProcess]:
    logger.info(f"$ {' '.join(str(c) for c in cmd)}")
    if dry_run:
        return None
    kwargs.setdefault("check", True)  # callers may override with check=False (e.g. docker rm/stop)
    return subprocess.run([str(c) for c in cmd], **kwargs)


def _lsolr() -> str:
    """Return the lsolr console-script path next to the current interpreter's venv."""
    candidate = Path(sys.executable).parent / "lsolr"
    return str(candidate) if candidate.exists() else "lsolr"


class SolrRuntime:
    """Start/stop Solr and tar its index over either docker or apptainer."""

    def __init__(self, cfg: SolrBuildConfig):
        """Resolve the runtime (docker/apptainer) for the given config."""
        self.cfg = cfg
        self.kind = detect_runtime(cfg.runtime, check=not cfg.dry_run)
        self._proc: Optional[subprocess.Popen] = None
        logger.info(f"solr runtime: {self.kind}")

    # -- lifecycle --------------------------------------------------------
    def start(self) -> None:
        """Launch Solr (detached) under the resolved runtime."""
        cfg = self.cfg
        solr_opts = f"-Dsolr.ramBufferSizeMB={cfg.ram_buffer_mb} -Dsolr.jetty.request.header.size=65535"
        if cfg.active_processors:
            solr_opts += f" -XX:ActiveProcessorCount={cfg.active_processors}"
        env_solr = {
            "SOLR_PORT": str(cfg.port),
            "SOLR_JAVA_MEM": f"-Xms{cfg.heap} -Xmx{cfg.heap}",
            "SOLR_OPTS": solr_opts,
        }
        if self.kind == "docker":
            _run(["docker", "rm", "-f", cfg.container], dry_run=cfg.dry_run, check=False)
            cmd = ["docker", "run", "-d", "--name", cfg.container, "-p", f"{cfg.port}:{cfg.port}", "-m", cfg.memory]
            for k, v in env_solr.items():
                cmd += ["-e", f"{k}={v}"]
            cmd += [cfg.image, "solr-foreground"]
            _run(cmd, dry_run=cfg.dry_run)
        else:  # apptainer
            sif = self._ensure_sif()
            if not cfg.dry_run:
                shutil.rmtree(cfg.solrhome, ignore_errors=True)
                cfg.solrhome.mkdir(parents=True, exist_ok=True)
            apptainer_env = os.environ.copy()
            for k, v in env_solr.items():
                apptainer_env[f"APPTAINERENV_{k}"] = v
            cmd = [
                "apptainer",
                "run",
                "--writable-tmpfs",
                "--bind",
                f"{cfg.solrhome}:/var/solr",
                str(sif),
                "solr-foreground",
            ]
            logger.info(f"$ {' '.join(cmd)} (backgrounded)")
            if not cfg.dry_run:
                log = open(cfg.solrhome / "solr.out", "wb")
                self._proc = subprocess.Popen(cmd, stdout=log, stderr=log, env=apptainer_env)

    def _ensure_sif(self) -> Path:
        cfg = self.cfg
        sif = cfg.sif or Path(".solr8.sif")
        if not sif.exists():
            _run(["apptainer", "pull", str(sif), f"docker://{cfg.image}"], dry_run=cfg.dry_run)
        return sif

    def stop(self) -> None:
        """Stop the running Solr (docker stop / terminate the apptainer process)."""
        if self.kind == "docker":
            _run(["docker", "stop", self.cfg.container], dry_run=self.cfg.dry_run, check=False)
        elif self._proc is not None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                self._proc.kill()

    def tar_index(self, dest: Path) -> None:
        """Tar the quiesced index. Solr must be committed & stopped before this.

        Compresses with pigz (parallel gzip) when available — single-threaded gzip
        of a multi-GB index is a serial tail nearly as long as the load itself.
        """
        cfg = self.cfg
        dest.parent.mkdir(parents=True, exist_ok=True)
        gz = "pigz" if shutil.which("pigz") else "gzip"
        if self.kind == "docker":
            # busybox tars the stopped container's volume uncompressed to stdout;
            # compress on the host so we can use the (parallel) pigz.
            src = f"docker run --rm --volumes-from {cfg.container} busybox tar cf - -C /var/solr data"
        else:  # apptainer: the host bind dir *is* /var/solr
            src = f"tar cf - -C {shlex.quote(str(cfg.solrhome))} data"
        cmd = f"{src} | {gz} > {shlex.quote(str(dest))}"
        logger.info(f"$ {cmd}")
        if not cfg.dry_run:
            subprocess.run(cmd, shell=True, check=True)
        if self.kind == "docker":
            _run(["docker", "rm", cfg.container], dry_run=cfg.dry_run, check=False)

    # -- readiness --------------------------------------------------------
    def wait_ready(self, timeout: int = 150) -> None:
        """Poll the Solr system endpoint until it answers or `timeout` elapses."""
        if self.cfg.dry_run:
            logger.info(f"[dry-run] skipping wait for {self.cfg.base_url}")
            return
        url = f"{self.cfg.base_url}/admin/info/system"
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                if requests.get(url, timeout=5).ok:
                    logger.info(f"Solr is ready at {self.cfg.base_url}")
                    return
            except requests.RequestException:
                pass
            time.sleep(5)
        raise RuntimeError(f"Solr did not become ready within {timeout}s")


# -- HTTP helpers (runtime-agnostic; replace the docker-exec add-cores etc.) ------


def _create_core(cfg: SolrBuildConfig, core: str) -> None:
    logger.info(f"create core {core}")
    if cfg.dry_run:
        return
    r = requests.get(
        f"{cfg.base_url}/admin/cores", params={"action": "CREATE", "name": core, "configSet": "_default"}, timeout=60
    )
    if not r.ok and "already exists" not in r.text:
        r.raise_for_status()


def _disable_tlog_and_reload(cfg: SolrBuildConfig, core: str) -> None:
    if cfg.dry_run:
        return
    requests.post(f"{cfg.base_url}/{core}/config", json={"set-property": {"updateLog.numRecordsToKeep": 0}}, timeout=60)
    requests.get(f"{cfg.base_url}/admin/cores", params={"action": "RELOAD", "core": core}, timeout=120)


def _commit(cfg: SolrBuildConfig, core: str) -> None:
    if cfg.dry_run:
        return
    requests.get(f"{cfg.base_url}/{core}/update", params={"commit": "true", "waitSearcher": "true"}, timeout=600)


def _unload_core(cfg: SolrBuildConfig, core: str) -> None:
    """Unload a core and delete its index/data/instance dirs (used to drop shard cores)."""
    if cfg.dry_run:
        return
    requests.get(
        f"{cfg.base_url}/admin/cores",
        params={
            "action": "UNLOAD",
            "core": core,
            "deleteIndex": "true",
            "deleteDataDir": "true",
            "deleteInstanceDir": "true",
        },
        timeout=120,
    )


def _run_schema_script(cfg: SolrBuildConfig, script: str) -> None:
    """Run one of the scripts/add_*.sh helpers, retargeted to this base URL.

    The bundled scripts hardcode localhost:8983; copy them with the port patched
    so a non-default port (or a second Solr) is never touched. TODO: port these
    ~200 lines of copy-field JSON into Python so the shell dependency goes away.
    """
    src = cfg.scripts_dir / script
    patched_dir = Path(".benchscripts")
    patched_dir.mkdir(exist_ok=True)
    patched = patched_dir / script
    text = src.read_text().replace("localhost:8983", f"{cfg.host}:{cfg.port}")
    patched.write_text(text)
    patched.chmod(0o755)
    _run(["bash", str(patched)], dry_run=cfg.dry_run, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _create_schema(cfg: SolrBuildConfig, core: str, top_class: str, schema: Path) -> None:
    _run(
        [_lsolr(), "create-schema", "-C", core, "-s", str(schema), "-u", cfg.base_url, "-t", top_class],
        dry_run=cfg.dry_run,
    )


def bulkload_core(cfg: SolrBuildConfig, core: str, table: str, schema: Path, where: Optional[str] = None) -> None:
    """Load one duckdb table into one core. The sharding seam.

    A sharded builder calls this N times with disjoint ``where`` predicates
    (e.g. ``hash(id) % N = j``) against N cores, then MERGEINDEXES to collapse.
    """
    cmd = [
        _lsolr(),
        "bulkload-db",
        "-C",
        core,
        "-s",
        str(schema),
        "-u",
        cfg.base_url,
        "--parallel-workers",
        str(cfg.parallel_workers),
        "--chunk-size",
        str(cfg.chunk_size),
    ]
    if where:
        cmd += ["--where", where]
    cmd += [str(cfg.duckdb), table]
    _run(cmd, dry_run=cfg.dry_run)


def _verify_counts(cfg: SolrBuildConfig) -> None:
    if cfg.dry_run:
        logger.info("[dry-run] skipping doc-count verification")
        return
    con = duckdb.connect(str(cfg.duckdb), read_only=True)
    failures = []
    for core, table in _VERIFY_SOURCE.items():
        expected = con.execute(f"SELECT count(DISTINCT id) FROM {table}").fetchone()[0]
        got = requests.get(f"{cfg.base_url}/{core}/select", params={"q": "*:*", "rows": 0}, timeout=120).json()[
            "response"
        ]["numFound"]
        status = "OK" if got == expected else "MISMATCH"
        logger.info(f"  {core}: numDocs={got:,} expected={expected:,} ({status})")
        if got != expected:
            failures.append(f"{core}: {got} indexed != {expected} expected ({table})")
    if failures:
        raise RuntimeError("Solr load incomplete:\n  - " + "\n  - ".join(failures))


def _resolve_sssom_schema() -> Path:
    import sssom_schema

    return Path(sssom_schema.__file__).parent / "schema" / "sssom_schema.yaml"


def build_solr(cfg: Optional[SolrBuildConfig] = None) -> None:
    """Port of scripts/load_solr.sh: build entity/association/sssom/infores cores."""
    cfg = cfg or SolrBuildConfig()

    if not cfg.schema.exists() and not cfg.dry_run:
        raise FileNotFoundError(f"{cfg.schema} not found — run `ingest merge` + `ingest closure` first.")
    sssom_schema = _resolve_sssom_schema()
    logger.info(f"SSSOM schema: {sssom_schema}")

    runtime = SolrRuntime(cfg)
    runtime.start()
    runtime.wait_ready()

    for core in ("entity", "association", "sssom", "infores"):
        _create_core(cfg, core)

    logger.info("adding field types")
    _run_schema_script(cfg, "add_fieldtypes.sh")

    _create_schema(cfg, "entity", "Entity", cfg.schema)
    _create_schema(cfg, "association", "Association", cfg.schema)
    # turn off the transaction log on the two big cores before bulk loading
    for core in ("entity", "association"):
        _disable_tlog_and_reload(cfg, core)
    _create_schema(cfg, "sssom", "mapping", sssom_schema)
    _create_schema(cfg, "infores", "InformationResource", cfg.infores_yaml)

    _run_schema_script(cfg, "add_entity_copyfields.sh")
    _run_schema_script(cfg, "add_association_copyfields.sh")

    # infores: load the jsonl directly (linkml-solr is unhappy with jsonl loading)
    logger.info("loading infores")
    if not cfg.dry_run:
        requests.post(
            f"{cfg.base_url}/infores/update/json/docs",
            params={"commit": "true"},
            data=cfg.infores_jsonl.read_bytes(),
            headers={"Content-Type": "application/json"},
            timeout=120,
        )

    bulkload_core(cfg, "sssom", "mappings", sssom_schema)
    bulkload_core(cfg, "entity", "denormalized_nodes", cfg.schema)
    bulkload_core(cfg, "association", "_solr_edges", cfg.schema)

    for core in ("entity", "association", "sssom", "infores"):
        _commit(cfg, core)

    logger.info("verifying core doc counts against source tables")
    _verify_counts(cfg)

    if cfg.skip_tarball:
        logger.info(f"skip_tarball set — leaving Solr running, not producing {cfg.tarball}")
        return

    logger.info("committing + stopping Solr, then tarring the index")
    runtime.stop()
    time.sleep(3)
    runtime.tar_index(cfg.tarball)
    logger.info(f"wrote {cfg.tarball}")


# ============================================================================
# Step 2: sharded build — parallelize one big core past a single IndexWriter.
#
# Shard the source table N ways by hash(id), load each shard core in parallel
# with our streaming loader (read-only, memory-capped, concurrent upload — no
# linkml-solr, no snapshot, no partition files), then MERGEINDEXES-collapse the
# N shard cores into one target core. The collapse copies segments (no
# re-analysis), so the expensive tokenization/copyfield work happens once, in
# parallel, in the shards. Sharding is the only way past a single Lucene
# IndexWriter's merge ceiling; on one node keep N <= cores/4 (each shard drives
# ~upload_workers analysis threads + merge_threads merge threads).
# ============================================================================


def install_default_configset(cfg: SolrBuildConfig, runtime_kind: str) -> None:
    """Copy the image's ``_default`` configset into SOLR_HOME (both runtimes).

    SOLR_HOME is /var/solr/data and starts empty (fresh apptainer bind, or a fresh
    docker container's var dir), so HTTP CREATE with configSet=_default can't find
    the configset — it only ships in the install dir at /opt/solr/... . Copy it in
    once before creating cores.
    """
    if cfg.dry_run:
        logger.info("[dry-run] would install _default configset into SOLR_HOME")
        return
    copy = (
        "mkdir -p /var/solr/data/configsets && "
        "cp -rn /opt/solr/server/solr/configsets/_default /var/solr/data/configsets/_default"
    )
    if runtime_kind == "docker":
        subprocess.run(["docker", "exec", cfg.container, "bash", "-c", copy], check=True)
    else:
        sif = cfg.sif or Path(".solr8.sif")
        subprocess.run(
            ["apptainer", "exec", "--bind", f"{cfg.solrhome}:/var/solr", str(sif), "bash", "-c", copy],
            check=True,
        )


def _cap_merge_threads(cfg: SolrBuildConfig) -> None:
    """Cap ConcurrentMergeScheduler threads in the installed configset's solrconfig.

    Without this, N shards spawn up to 4N merge threads and thrash the node.
    Cores copy the configset at CREATE time, so edit it before creating shards.
    """
    conf = cfg.solrhome / "data" / "configsets" / "_default" / "conf" / "solrconfig.xml"
    if cfg.dry_run or not conf.exists():
        return
    text = conf.read_text()
    if "<mergeScheduler" in text:
        return
    ms = (
        '<mergeScheduler class="org.apache.lucene.index.ConcurrentMergeScheduler">'
        f'<int name="maxThreadCount">{cfg.merge_threads}</int>'
        '<int name="maxMergeCount">6</int></mergeScheduler>'
    )
    if "<indexConfig>" in text:
        text = text.replace("<indexConfig>", "<indexConfig>\n    " + ms, 1)
    else:
        text = text.replace("</config>", f"  <indexConfig>\n    {ms}\n  </indexConfig>\n</config>", 1)
    conf.write_text(text)


def _add_fieldtypes_to_core(cfg: SolrBuildConfig, core: str) -> None:
    """POST the custom field-type definitions to one specific core."""
    if cfg.dry_run:
        return
    for f in (
        "text-fieldtype.json",
        "autocomplete-fieldtype.json",
        "grounding-fieldtype.json",
        "sortable-float-fieldtype.json",
    ):
        requests.post(
            f"{cfg.base_url}/{core}/schema",
            data=(cfg.scripts_dir / f).read_bytes(),
            headers={"Content-Type": "application/json"},
            timeout=60,
        )


def _add_copyfields_to_core(cfg: SolrBuildConfig, core: str, script: str) -> None:
    """Retarget a scripts/add_*_copyfields.sh to one specific core + port, run it.

    When a column is pre-analyzed, drop it from the copyField loop — the loader
    populates its _t field with pre-analyzed tokens, and copying the raw value in
    would fail to parse as pre-analyzed JSON.
    """
    text = (cfg.scripts_dir / script).read_text()
    text = text.replace("localhost:8983", f"{cfg.host}:{cfg.port}").replace("/solr/association/", f"/solr/{core}/")
    for raw_col, _ in cfg.preanalyze_map:
        text = text.replace(f" {raw_col}\n", "\n").replace(f" {raw_col} ", " ")
    d = Path(".benchscripts")
    d.mkdir(exist_ok=True)
    patched = d / f"cf_{core}.sh"
    patched.write_text(text)
    patched.chmod(0o755)
    _run(["bash", str(patched)], dry_run=cfg.dry_run, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _setup_shard_core(cfg: SolrBuildConfig, core: str) -> None:
    """Create one shard/target core with the full association schema."""
    _create_core(cfg, core)
    _add_fieldtypes_to_core(cfg, core)
    _create_schema(cfg, core, cfg.sharded_top_class, cfg.schema)
    _disable_tlog_and_reload(cfg, core)
    _add_copyfields_to_core(cfg, core, cfg.sharded_copyfields)
    if cfg.preanalyze_map:
        _setup_preanalyzed_fields(cfg, core)


def _preanalyze(base: str, core: str, fieldtype: str, sess: requests.Session, label: str) -> str:
    """Return the Solr JsonPreAnalyzedParser serialization of `label` under `fieldtype`."""
    r = sess.get(
        f"{base}/{core}/analysis/field",
        params={"analysis.fieldtype": fieldtype, "analysis.fieldvalue": label, "wt": "json"},
        timeout=30,
    )
    final = r.json()["analysis"]["field_types"][fieldtype]["index"][-1]
    toks = [
        {
            "t": t["text"],
            "s": t.get("start"),
            "e": t.get("end"),
            "i": t["positionIncrement"] if isinstance(t.get("positionIncrement"), int) else 1,
        }
        for t in final
    ]
    return json.dumps({"v": "1", "str": label, "tokens": toks})


def build_preanalyzed_cache(cfg: SolrBuildConfig) -> Optional[Path]:
    """Analyze each DISTINCT closure-label value once; write {value: preanalyzed_json} to disk.

    Returns the cache path (workers load it), or None if pre-analysis is off. Solr
    must be up (uses its analysis endpoint against `preanalyze_via_fieldtype`).
    """
    if not cfg.preanalyze_map or cfg.dry_run:
        return None
    raw_cols = [raw for raw, _ in cfg.preanalyze_map]
    con = duckdb.connect(str(cfg.duckdb), read_only=True)
    unions = " UNION ".join(f"SELECT DISTINCT unnest({c}) AS v FROM {cfg.sharded_table}" for c in raw_cols)
    labels = [r[0] for r in con.execute(f"SELECT DISTINCT v FROM ({unions}) t WHERE v IS NOT NULL").fetchall()]
    logger.info(f"pre-analyzing {len(labels):,} distinct label values (once, vs re-analyzing every occurrence)")
    sess = requests.Session()
    sess.mount(cfg.base_url, HTTPAdapter(pool_connections=24, pool_maxsize=48))

    def one(label):
        return label, _preanalyze(cfg.base_url, cfg.sharded_target, cfg.preanalyze_via_fieldtype, sess, label)

    cache = {}
    with ThreadPoolExecutor(max_workers=24) as ex:
        for label, js in ex.map(one, labels):
            cache[label] = js
    dest = Path(".preanalyzed_cache.json")
    dest.write_text(json.dumps(cache))
    logger.info(f"wrote pre-analyzed cache: {len(cache):,} entries -> {dest}")
    return dest


def _setup_preanalyzed_fields(cfg: SolrBuildConfig, core: str) -> None:
    """Add the preanalyzed_text type and define the *_closure_label_t fields as it."""
    if cfg.dry_run:
        return
    requests.post(
        f"{cfg.base_url}/{core}/schema",
        data=(cfg.scripts_dir / "preanalyzed-fieldtype.json").read_bytes(),
        headers={"Content-Type": "application/json"},
        timeout=60,
    )
    for _, t_field in cfg.preanalyze_map:
        requests.post(
            f"{cfg.base_url}/{core}/schema",
            json={
                "add-field": {
                    "name": t_field,
                    "type": "preanalyzed_text",
                    "indexed": True,
                    "stored": False,
                    "multiValued": True,
                }
            },
            timeout=60,
        )


def _load_shard_worker(a: tuple) -> tuple:
    """Stream one core's rows (optionally a `WHERE hash(id) % N = j` slice).

    Module-level (picklable) so ProcessPoolExecutor can fan it out. Reads the
    duckdb read-only with a capped memory_limit and streams fetchmany(batch)
    rows, POSTing batches through a thread pool for upload concurrency. With
    ``where=None`` it loads the whole table into ``core`` (the N=1 direct path,
    no shard/merge). If ``preanalyze`` (a (raw_col, t_field) list) and a cache
    path are given, the *_t fields are populated with pre-analyzed tokens from the
    cache instead of relying on copyField re-analysis.
    """
    duckdb_path, base, core, table, where, mem, batch, workers, preanalyze, cache_path = a
    con = duckdb.connect(duckdb_path, read_only=True)
    con.execute(f"SET memory_limit='{mem}'")
    con.execute("SET threads=2")
    query = f"SELECT * FROM {table}" + (f" WHERE {where}" if where else "")
    cur = con.execute(query)
    cols = [d[0] for d in cur.description]
    url = f"{base}/{core}/update/json/docs"
    sess = requests.Session()
    sess.mount(base, HTTPAdapter(pool_connections=workers, pool_maxsize=workers * 2))
    cache = json.loads(Path(cache_path).read_text()) if cache_path else {}

    def build_doc(row) -> dict:
        doc = {c: v for c, v in zip(cols, row) if v is not None}
        for raw_col, t_field in preanalyze:
            vals = doc.get(raw_col)
            if vals:
                doc[t_field] = [cache[v] for v in vals if v in cache]
        return doc

    def post(docs: list) -> int:
        r = sess.post(
            url,
            params={"commit": "false"},
            data=json.dumps(docs, default=str),
            headers={"Content-Type": "application/json"},
            timeout=300,
        )
        r.raise_for_status()
        return len(docs)

    total, t0 = 0, time.time()
    inflight: set = set()
    cap = workers * 2
    with ThreadPoolExecutor(max_workers=workers) as ex:
        while True:
            rows = cur.fetchmany(batch)
            if not rows:
                break
            docs = [build_doc(row) for row in rows]
            inflight.add(ex.submit(post, docs))
            if len(inflight) >= cap:
                done, inflight = wait(inflight, return_when=FIRST_COMPLETED)
                total += sum(f.result() for f in done)
        for f in as_completed(inflight):
            total += f.result()
    sess.get(f"{base}/{core}/update", params={"commit": "true", "waitSearcher": "true"}, timeout=600)
    dt = time.time() - t0
    return core, total, round(dt, 1), round(total / dt) if dt else 0


def _numfound(cfg: SolrBuildConfig, core: str) -> int:
    r = requests.get(f"{cfg.base_url}/{core}/select", params={"q": "*:*", "rows": 0}, timeout=120)
    return r.json()["response"]["numFound"]


def merge_indexes(cfg: SolrBuildConfig, target: str, sources: list, expected: Optional[int] = None) -> None:
    """MERGEINDEXES the source cores into ``target`` (segment copy, no re-analysis).

    Robust to a dropped connection: a large merge runs server-side on the Lucene
    writer thread and can outlive the HTTP request (Jetty may close a long-blocked
    request that sends no response bytes). So fire the request, tolerate a
    disconnect, and *poll* the target doc count until the merge lands — never
    blindly retry the merge (addIndexes is not idempotent; it would duplicate ids).
    """
    if cfg.dry_run:
        logger.info(f"[dry-run] would MERGEINDEXES {sources} -> {target}")
        return
    src = "".join(f"&srcCore={s}" for s in sources)
    url = f"{cfg.base_url}/admin/cores?action=mergeindexes&core={target}{src}"
    logger.info(f"MERGEINDEXES {len(sources)} shards -> {target} (polling for completion)")
    try:
        requests.get(url, timeout=(30, cfg.merge_timeout))
    except requests.exceptions.RequestException as e:
        logger.warning(f"mergeindexes connection dropped ({e}); merge continues server-side, polling")

    deadline = time.time() + cfg.merge_timeout
    last = -1
    while time.time() < deadline:
        _commit(cfg, target)
        got = _numfound(cfg, target)
        logger.info(f"  merged {got:,}" + (f"/{expected:,}" if expected is not None else ""))
        if expected is not None and got >= expected:
            return
        if expected is None and got > 0 and got == last:
            return  # count stabilized and no expected target given
        last = got
        time.sleep(30)
    raise RuntimeError(f"MERGEINDEXES did not complete within {cfg.merge_timeout}s (target has {got})")


def build_solr_sharded(cfg: Optional[SolrBuildConfig] = None) -> None:
    """Sharded build of one big core (default: association / _solr_edges)."""
    cfg = cfg or SolrBuildConfig()
    if cfg.n_shards < 1:
        raise ValueError("n_shards must be >= 1")
    if not cfg.schema.exists() and not cfg.dry_run:
        raise FileNotFoundError(f"{cfg.schema} not found — run `ingest merge` + `ingest closure` first.")

    runtime = SolrRuntime(cfg)
    runtime.start()
    runtime.wait_ready()
    install_default_configset(cfg, runtime.kind)  # SOLR_HOME starts empty under both runtimes
    if runtime.kind == "apptainer":
        _cap_merge_threads(cfg)  # docker keeps the configset in-container; rely on small N instead

    # N=1 loads straight into the target — no shard cores, no collapse (the merge is
    # CPU/throttle-bound, not I/O-bound, so on a single machine it's pure overhead).
    sharded = cfg.n_shards > 1
    shards = [f"shard_{j}" for j in range(cfg.n_shards)] if sharded else []
    load_cores = shards if sharded else [cfg.sharded_target]

    logger.info(f"setting up {'%d shard cores + ' % cfg.n_shards if sharded else ''}target '{cfg.sharded_target}'")
    for core in ([*shards, cfg.sharded_target] if sharded else [cfg.sharded_target]):
        _setup_shard_core(cfg, core)

    cache_path = str(build_preanalyzed_cache(cfg)) if cfg.preanalyze_map else None

    mode = f"{cfg.n_shards} shards" if sharded else "direct (N=1, no merge)"
    logger.info(f"streaming load: {mode} x {cfg.upload_workers} upload threads")
    if not cfg.dry_run:
        args = [
            (
                str(cfg.duckdb),
                cfg.base_url,
                core,
                cfg.sharded_table,
                (f"hash(id) % {cfg.n_shards} = {j}" if sharded else None),
                cfg.duckdb_memory_limit,
                cfg.batch_size,
                cfg.upload_workers,
                cfg.preanalyze_map,
                cache_path,
            )
            for j, core in enumerate(load_cores)
        ]
        with ProcessPoolExecutor(max_workers=len(load_cores)) as ex:
            results = list(ex.map(_load_shard_worker, args))
        loaded = 0
        for core, total, secs, dps in sorted(results):
            loaded += total
            logger.info(f"  {core}: {total:,} docs in {secs}s ({dps:,}/s)")
        logger.info(f"loaded {loaded:,} across {len(load_cores)} core(s)")

    expected = None
    if not cfg.dry_run:
        con = duckdb.connect(str(cfg.duckdb), read_only=True)
        expected = con.execute(f"SELECT count(DISTINCT id) FROM {cfg.sharded_table}").fetchone()[0]

    if sharded:
        logger.info(f"collapse: MERGEINDEXES {cfg.n_shards} shards -> {cfg.sharded_target}")
        merge_indexes(cfg, cfg.sharded_target, shards, expected=expected)

    if not cfg.dry_run:
        got = _numfound(cfg, cfg.sharded_target)
        status = "OK" if got == expected else "MISMATCH"
        logger.info(f"{cfg.sharded_target}: numDocs={got:,} expected={expected:,} ({status})")
        if got != expected:
            raise RuntimeError(f"sharded load incomplete: {got} != {expected}")

    # Drop the intermediate shard cores (index + dirs) so the tarball contains only
    # the merged target, not N redundant copies of the same data.
    if sharded:
        logger.info(f"unloading {cfg.n_shards} intermediate shard cores")
        for core in shards:
            _unload_core(cfg, core)

    if cfg.skip_tarball:
        logger.info(f"skip_tarball set — leaving Solr running, not producing {cfg.tarball}")
        return
    runtime.stop()
    time.sleep(3)
    runtime.tar_index(cfg.tarball)
    logger.info(f"wrote {cfg.tarball}")
