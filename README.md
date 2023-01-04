# Monarch Ingest

| [Documentation](https://monarch-initiative.github.io/monarch-ingest/) |

Monarch Ingest is a data-ingest application for Monarch Initiative using Koza. 

# Neo4j Database Loading

Docker Compose may be used to initialize and run a local Neo4j instance of Monarch.  It is assumed that you have already [installed Docker](https://docs.docker.com/get-docker/) and [Compose](https://docker-docs.netlify.app/compose/install/) or perhaps have the [Docker Desktop](https://docs.docker.com/compose/install/) running on your local system.

## Download Data

We currently get the latest Monarch Neo4j data dump from 
[here](https://data.monarchinitiative.org/monarch-kg-dev/latest/monarch-kg.neo4j.dump). The `download_monarch_scigraph_neo4j_dump.sh` (under **scripts**) can be used to download the data directly into the project's '**dumps**' folder, for subsequent loading. Optional command line arguments for the filename (default: **monarch-kg.neo4j.dump**) and the source base URL (default: **https://data.monarchinitiative.org/monarch-kg-dev/latest**) may be given, to download Neo4j data dumps from other sources.

## Configuration

Copy the **`dot_env_template`** file (found in the root project directory) into a **`.env`** ("dot env") file. This copy of the **.env** is **.gitignore'd**.

Uncomment the **`DO_LOAD=1`** in the **.env** file to trigger loading upon Docker (Compose) startup.  Note that the database is persisted in between Docker builds, within the local directory **neo4j-data** (mapped to a Docker volume) thus the **`DO_LOAD`** can be commented out or set back to zero after initial data loading. 

Optionally, if the name of the data file you downloaded above is _**not**_ named `monarch-kg.neo4j.dump`, then uncomment the **NEO4J_DUMP_FILENAME** environment variable and set it to the actual file name (i.e. the name of the file that you downloaded into the local **dumps** folder).

In addition, even if unmodified, a copy must be made of the **neo4j.conf-template** file in the **neo4j** directory (relative to the root project directory) into a [neo4j.conf](./neo4j/neo4j.conf) of [Neo4j Configuration Settings](https://neo4j.com/docs/operations-manual/current/reference/configuration-settings) file (in the same directory), to which the Docker Compose yaml configuration file (below) specifies a volume reference. 

Note that this file copy is **.gitignore'd**, but may now be tweaked for site-specific purposes. For example:

```properties
dbms.databases.default_to_read_only=true
```

Sets the Neo4j instance to be 'read only' by default.

```properties
dbms.security.auth_enabled=true
```

Sets the Neo4j instance to enforce authentication. Set to 'false' if you wish to override this.

See [neo4j configuration settings page](https://neo4j.com/docs/operations-manual/4.4/reference/configuration-settings/) for details about other settings.

## Running the System

First, make sure that Docker (or the Docker Desktop) is running then Docker Compose is used to build the local Monarch Neo4j system. From the monarch-ingest project root directory, type commands as follows:

```bash
# May not normally be necessary since the Docker Compose system
# currently uses 'canned' Docker images for its containers.
docker-compose build
```

Then start up the system (as a background daemon):

```bash
docker-compose up -d
```

To monitor the logs:

```bash
docker-compose logs -f
```

To stop the server:

```bash
docker-compose down
```

The Neo4j instances with Monarch data loaded should now be visible at **http://localhost:7474**.
