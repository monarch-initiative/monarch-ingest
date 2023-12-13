#!/bin/sh

# Add two dynamicfields declarations to the schema

# One for text fields, have to replace because _t comes built in

# delete the _t dynamic field
curl -X POST -H 'Content-type:application/json' --data-binary '{
    "delete-dynamic-field": {
        "name": "*_t"
    }
}' http://localhost:8983/solr/entity/schema

curl -X POST -H 'Content-type:application/json' --data-binary '{
    "add-dynamic-field": {
        "name": "*_t",
        "type": "text",
        "indexed": true,
        "stored": false,
        "multiValued": true
    }
}' http://localhost:8983/solr/entity/schema

# One for autocomplete fields

curl -X POST -H 'Content-type:application/json' --data-binary '{
    "add-dynamic-field": {
        "name": "*_ac",
        "type": "autocomplete",
        "indexed": true,
        "stored": false,
        "multiValued": true
    }
}' http://localhost:8983/solr/entity/schema


# now add copyfields declarations for name, symbol and synonym

# name

curl -X POST -H 'Content-type:application/json' --data-binary '{
    "add-copy-field": {
        "source": "name",
        "dest": "name_t"
    }
}' http://localhost:8983/solr/entity/schema

curl -X POST -H 'Content-type:application/json' --data-binary '{
    "add-copy-field": {
        "source": "name",
        "dest": "name_ac"
    }
}' http://localhost:8983/solr/entity/schema

# symbol

curl -X POST -H 'Content-type:application/json' --data-binary '{
    "add-copy-field": {
        "source": "symbol",
        "dest": "symbol_t"
    }
}' http://localhost:8983/solr/entity/schema

curl -X POST -H 'Content-type:application/json' --data-binary '{
    "add-copy-field": {
        "source": "symbol",
        "dest": "symbol_ac"
    }
}' http://localhost:8983/solr/entity/schema

# synonym

curl -X POST -H 'Content-type:application/json' --data-binary '{
    "add-copy-field": {
        "source": "synonym",
        "dest": "synonym_t"
    }
}' http://localhost:8983/solr/entity/schema

curl -X POST -H 'Content-type:application/json' --data-binary '{
    "add-copy-field": {
        "source": "synonym",
        "dest": "synonym_ac"
    }
}' http://localhost:8983/solr/entity/schema

# taxon label

curl -X POST -H 'Content-type:application/json' --data-binary '{
    "add-copy-field": {
        "source": "in_taxon_label",
        "dest": "in_taxon_label_t"
    }
}' http://localhost:8983/solr/entity/schema

curl -X POST -H 'Content-type:application/json' --data-binary '{
    "add-copy-field": {
        "source": "in_taxon_label",
        "dest": "in_taxon_label_ac"
    }
}' http://localhost:8983/solr/entity/schema

# taxon id

curl -X POST -H 'Content-type:application/json' --data-binary '{
    "add-copy-field": {
        "source": "in_taxon",
        "dest": "in_taxon_t"
    }
}' http://localhost:8983/solr/entity/schema

# description

curl -X POST -H 'Content-type:application/json' --data-binary '{
    "add-copy-field": {
        "source": "description",
        "dest": "description_t"
    }
}' http://localhost:8983/solr/entity/schema

# xref

curl -X POST -H 'Content-type:application/json' --data-binary '{
    "add-copy-field": {
        "source": "xref",
        "dest": "xref_t"
    }
}' http://localhost:8983/solr/entity/schema
