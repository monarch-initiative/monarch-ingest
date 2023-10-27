#!/bin/sh

# Add two dynamicfields declarations to the schema

# One for text fields, have to replace because _t comes built in

# delete the _t dynamic field
curl -X POST -H 'Content-type:application/json' --data-binary '{
    "delete-dynamic-field": {
        "name": "*_t"
    }
}' http://localhost:8983/solr/association/schema

curl -X POST -H 'Content-type:application/json' --data-binary '{
    "add-dynamic-field": {
        "name": "*_t",
        "type": "text",
        "indexed": true,
        "stored": false,
        "multiValued": true
    }
}' http://localhost:8983/solr/association/schema

# One for autocomplete fields

curl -X POST -H 'Content-type:application/json' --data-binary '{
    "add-dynamic-field": {
        "name": "*_ac",
        "type": "autocomplete",
        "indexed": true,
        "stored": false,
        "multiValued": true
    }
}' http://localhost:8983/solr/association/schema


# now add copyfields declarations for subject_label, subject_closure_label, object_label, object_closure_label

for field in subject_label subject_closure_label subject_taxon subject_taxon_label predicate object_label object_closure_label object_taxon object_taxon_label primary_knowledge_source qualifiers_label onset_qualifier_label frequency_qualifier_label sex_qualifier_label
do
  curl -X POST -H 'Content-type:application/json' --data-binary "{
  \"add-copy-field\": {
      \"source\":\"$field\",
      \"dest\": \"${field}_t\"
  }
}" http://localhost:8983/solr/association/schema
done
