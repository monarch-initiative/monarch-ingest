# Running a Dockerized Neo4j Instance of Monarch

With suitable configuration, a Docker Compose may be used to initialize and run a local Neo4j instance of Monarch.  It is assumed that you have already [installed Docker](https://docs.docker.com/get-docker/) and [Compose](https://docker-docs.netlify.app/compose/install/) or perhaps have the [Docker Desktop](https://docs.docker.com/compose/install/) running on your local system.

## Download Data

We currently get the latest Monarch Neo4j data dump from 
[here](https://data.monarchinitiative.org/monarch-kg-dev/latest/monarch-kg.neo4j.dump). The `download_monarch_scigraph_neo4j_dump.sh` (under **scripts**) can be used to download the data directly into the project's '**dumps**' folder, for subsequent loading. Optional command line arguments for the filename (default: **monarch-kg.neo4j.dump**) and the source base URL (default: **https://data.monarchinitiative.org/monarch-kg-dev/latest**) may be given, to download Neo4j data dumps from other sources.

## Basic Neo4j Instance Configuration

Copy the **`dot_env_template`** file (found in the root project directory) into a **`.env`** ("dot env") file. This copy of the **.env** is **.gitignore'd**.

Uncomment the **`DO_LOAD=1`** in the **.env** file to trigger loading upon Docker (Compose) startup.  Note that the database is persisted in between Docker builds, within the local directory **neo4j-data** (mapped to a Docker volume) thus the **`DO_LOAD`** can be commented out or set back to zero after initial data loading. 

Optionally, if the name of the data file you downloaded above is _**not**_ named `monarch-kg.neo4j.dump`, then uncomment the **NEO4J_DUMP_FILENAME** environment variable and set it to the actual file name (i.e. the name of the file that you downloaded into the local **dumps** folder).

In addition, even if unmodified, a copy must be made of the **neo4j.conf-template** file found in the **neo4j/conf** directory (relative to the root project directory) into an instance of **neo4j.conf** file in the same location, named [neo4j/conf/neo4j.conf](neo4j/conf/neo4j.conf) of [Neo4j Configuration Settings](https://neo4j.com/docs/operations-manual/current/reference/configuration-settings) file (in the same directory), to which the Docker Compose yaml configuration file (below) specifies a volume reference. 

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

First, make sure that Docker (or the Docker Desktop) is running then Docker Compose is used to build the local Monarch Neo4j system. Note that since we are simply directly using a standard Neo4j Docker image from DockerHub, there is no 'build' step needed.

Initially, we may be running the Neo4j instance off regular HTTP. The necessary Compose configuration is in the default **docker-compose.yaml** file, thus, to start up the system (as a background daemon), we simply type:

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

## HTTPS/SSL Wrapping of the Neo4j Server Instance

See the [online Neo4j SSL encryption docs](https://neo4j.com/docs/operations-manual/current/docker/security/) for full details.

The steps are essentially as follows:

1. Obtain SSL public certificates and private keys from a trusted certificate authority such as [https://www.openssl.org/](https://www.openssl.org/) or [https://letsencrypt.org/](https://letsencrypt.org/). Distinct certificates for the different communication channels (**`bolt`** and **`https`**) are recommended.

2. Place these distinct (**`bolt`** and **`https`**) certificates and keys into the corresponding subdirectory of the communication scope (**`bolt`** or **`https`**) under the [neo4j/certificates](neo4j/certificates) directory of the project. For example, place the **`bolt`** certificates and keys under [neo4j/certificates/bolt](neo4j/certificates/bolt).

3. Ensure that the following settings are uncommented in the **neo4j.conf** file, to configure the following settings for the policies to be used:

```properties
# Https SSL configuration
dbms.connector.https.enabled=true
dbms.ssl.policy.https.enabled=true
dbms.ssl.policy.https.base_directory=certificates/https
dbms.ssl.policy.https.private_key=private.key
dbms.ssl.policy.https.public_certificate=public.crt


# Bolt SSL configuration
dbms.ssl.policy.bolt.enabled=true
dbms.ssl.policy.bolt.base_directory=certificates/bolt
dbms.ssl.policy.bolt.private_key=private.key
dbms.ssl.policy.bolt.public_certificate=public.crt
```

4. (Re-)start the Docker container (i.e. using Compose). Note that since the above SSL configuration changes are external to the image itself, there is generally no need to (re-)build the system before (re-)running it for SSL secured access (once the certificates and private keys are in place). However, we need to substitute a Docker Compose YAML file configured for SSL/HTTPS encryption of Neo4j (**docker-compose-ssl.yaml**) is slightly different from its (default) HTTP counterpart. Thus, to run the SSL secured system (after the above configuration steps), we type:

```bash
docker-compose -f docker-compose-ssl.yaml up -d
```

Of course, substitute in the same **docker-compose-ssl.yaml** file for the corresponding **Compose** `logs` and `down` commands.
