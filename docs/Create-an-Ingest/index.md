# Ingests

!!! tip "Ingest Overview"
    An ingest consists of 2 main steps:  

    - Downloading the data  
    - Transforming the data  

    With 2 post-processing steps:

    - Merging the output into a KGX knowledge graph
    - Releasing the result to the Monarch Initiative Google Cloud bucket

**Let's go through the process for running an existing monarch ingest!**

!!! list ""
    **Step 1. Download**

    - Download the dataset for your ingest, for example:
        ```bash
        ingest download --tags ncbi_gene
        ```

        or to download all source data:
        ```bash
        ingest download --all
        ```

    **Step 2. Transform**

    - Transform the data, for example:
        ```bash
        ingest transform --tag ncbi_gene --row-limit 20 --log
        ```

        or 

        ```bash
        ingest transform --all
        ```

    **Step 3. Merge**

    - This step is typically performed after `ingest transform --all`, and merges all output node and edge files into a tar.gz containing one node and one edge file:
        ```bash
        ingest merge
        ```

    **Step 4. Release**

    - Once you've transformed all the data and merged the output, you can create and upload a release:
        ```bash
        ingest release
        ```

--  
**Now let's look at how to create and add a new ingest! First step: [Configure](Configure.md)**
