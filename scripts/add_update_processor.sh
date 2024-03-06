#!/bin/sh

# Upload the script file to the Solr server
#curl -X POST -H 'Content-type:application/octet-stream' --data-binary @scripts/frequency_update_processor.js http://localhost:8983/solr/association/config/scripts/frequency_update_processor.js

#The post command above fails, but it works to do a docker cp:
docker cp scripts/frequency_update_processor.js my_solr:/var/solr/data/association/

# Add the script to the update processor chain
curl -X POST -H 'Content-type:application/json' -d '{
  "add-updateprocessor": {
    "name": "frequency_update_processor",
    "class": "solr.StatelessScriptUpdateProcessorFactory",
    "script": "frequency_update_processor.js"
  }
}' http://localhost:8983/solr/association/config

curl -X POST -H 'Content-type:application/json' -d '{
  "add-updateprocessor": {
    "name": "default",
    "processor": ["frequency_update_processor"],
    "class": "solr.RunUpdateProcessorFactory"
  }
}' http://localhost:8983/solr/association/config