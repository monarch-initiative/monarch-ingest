#!/bin/bash

gsutil ls gs://data-public-monarchinitiative/monarch-kg-dev/latest/ | grep -Eo "(\d){4}-(\d){2}-(\d){2}"
