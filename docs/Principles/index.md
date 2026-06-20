# Ingest Principles

## Overview

The Monarch Knowledge Graph (KG) is built from a variety of data sources in the biomedical domain.
These data sources are "ingested" into the KG using a variety of tools and packages created by the Monarch Initiative team and our collaborators.
This page describes the principles that guide the ingestion process.

A list of all data sources ingested into the KG can be found [here](../Sources/index.md).

## General Principles

1. All ingests should have a stringent (defensive) filtering strategy.

1. Utilize Biolink profiles to inform the filtering of incoming ingests (ex. Phenio)

1. Use yaml to implement this

1. All nodes should have a category attached.
