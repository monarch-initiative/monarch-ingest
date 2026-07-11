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

import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import duckdb
import requests

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
    ram_buffer_mb: int = 2048
    parallel_workers: int = 4
    chunk_size: int = 100_000

    skip_tarball: bool = False  # SOLR_SKIP_TARBALL=1 equivalent
    tarball: Path = Path("output/solr.tar.gz")
    scripts_dir: Path = Path("scripts")
    dry_run: bool = False

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
    return subprocess.run([str(c) for c in cmd], check=True, **kwargs)


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
        env_solr = {
            "SOLR_PORT": str(cfg.port),
            "SOLR_JAVA_MEM": f"-Xms{cfg.heap} -Xmx{cfg.heap}",
            "SOLR_OPTS": f"-Dsolr.ramBufferSizeMB={cfg.ram_buffer_mb} -Dsolr.jetty.request.header.size=65535",
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
        """Tar the quiesced index. Solr must be committed & stopped before this."""
        cfg = self.cfg
        dest.parent.mkdir(parents=True, exist_ok=True)
        if self.kind == "docker":
            # index is quiet on disk in the stopped container's volume; tar via a sidecar
            with open(dest, "wb") as fh:
                if cfg.dry_run:
                    logger.info(
                        f"$ docker run --rm --volumes-from {cfg.container} busybox "
                        f"tar czf - -C /var/solr data > {dest}"
                    )
                else:
                    subprocess.run(
                        [
                            "docker",
                            "run",
                            "--rm",
                            "--volumes-from",
                            cfg.container,
                            "busybox",
                            "tar",
                            "czf",
                            "-",
                            "-C",
                            "/var/solr",
                            "data",
                        ],
                        stdout=fh,
                        check=True,
                    )
            _run(["docker", "rm", cfg.container], dry_run=cfg.dry_run, check=False)
        else:  # apptainer: the host bind dir *is* /var/solr
            _run(["tar", "czf", str(dest), "-C", str(cfg.solrhome), "data"], dry_run=cfg.dry_run)

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
