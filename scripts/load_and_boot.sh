#!/bin/bash

[ ${DO_LOAD} -eq 1 ] && neo4j-admin load /dumps/db.dump
tini -g -- /startup/docker-entrypoint.sh
