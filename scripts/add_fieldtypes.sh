#!/bin/bash

for core in entity association
do
  curl -X POST -H 'Content-type:application/json' -d @scripts/text-fieldtype.json http://localhost:8983/solr/$core/schema
  curl -X POST -H 'Content-type:application/json' -d @scripts/autocomplete-fieldtype.json http://localhost:8983/solr/$core/schema
done
