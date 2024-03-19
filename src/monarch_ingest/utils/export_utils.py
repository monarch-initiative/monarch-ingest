
""" Monarch Data Dump

This script is used to dump tsv files from the
Monarch association index

The input is a yaml configuration with the format:

directory_name:
  file_name.tsv:
  - solr_filter_1
  - solr_filter_2
"""
import json
from json import decoder
from enum import Enum
from pathlib import Path
import logging
import yaml
import gzip
import time
import re

import requests
from requests.exceptions import ChunkedEncodingError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OutputType(str, Enum):
    tsv = 'tsv'
    jsonl = 'jsonl'


OUTPUT_TYPES = set(OutputType._member_names_)


def export(config_file: str = "./src/monarch_ingest/data-dump-config.yaml",
           output_dir: str = "./output/tsv/",
           output_format: OutputType = OutputType.tsv,
           solr_url: str = "http://localhost:8983/solr/association/select"):

    if output_format not in OUTPUT_TYPES:
        raise ValueError(f"output format not supported, supported formats are {OUTPUT_TYPES}")

    dir_path = Path(output_dir)

    # Fetch all associations
    association_dir = 'all_associations'
    dump_dir = dir_path / association_dir
    dump_dir.mkdir(parents=True, exist_ok=True)

    # wt=json&facet=true&json.nl=arrarr&rows=0&q=*:*&facet.field=association_type
    assoc_params = {
        'q': '*:*',
        'wt': 'json',
        'json.nl': 'arrarr',
        'rows': 0,
        'facet': 'true',
        'facet.field': 'category'
    }

    solr_request = requests.get(solr_url, params=assoc_params)
    response = solr_request.json()
    solr_request.close()

    for facet in reversed(response['facet_counts']['facet_fields']['category']):
        association = facet[0]
        category_name = camel_to_snake(re.sub(r'biolink:', '', association))
        # quote the facet value because of the biolink: prefix
        association = f'"{association}"'
        print(association)
        file = f"{category_name}.all.{output_format}.gz"
        dump_file_fh = gzip.open(dump_dir / file, 'wt')
        filters = ['category:{}'.format(association)]

        if output_format == 'tsv':
            generate_tsv(dump_file_fh, solr_url, filters)
        elif output_format == 'jsonl':
            generate_jsonl(dump_file_fh, solr_url, filters)

        logger.info(f"finished writing {file}")

    # Fetch associations configured in config_file
    conf_fh = open(config_file, 'r')
    file_filter_map = yaml.safe_load(conf_fh)

    for directory, file_maps in file_filter_map.items():
        dump_dir = dir_path / directory
        dump_dir.mkdir(parents=True, exist_ok=True)

        for file, filters in file_maps.items():
            dump_file = dump_dir / file
            dump_file_fh = gzip.open(dump_file, 'wt')

            if output_format == 'tsv':
                generate_tsv(dump_file_fh, solr_url, filters)
            elif output_format == 'jsonl':
                generate_jsonl(dump_file_fh, solr_url, filters)

            dump_file_fh.close()


def generate_tsv(tsv_fh, solr, filters):
    default_fields = ','.join([
            'subject',
            'subject_label',
            'subject_taxon',
            'subject_taxon_label',
            'negated',
            'predicate',
            'object',
            'object_label',
            'qualifier'
            'publications',
            'has_evidence',
            'primary_knowledge_source',
            'aggregator_knowledge_source',
        ])
    disease_to_phenotype_extra_fields = ','.join([
        'onset_qualifier',
        'onset_qualifier_label',
        'frequency_qualifier',
        'frequency_qualifier_label',
        'sex_qualifier',
        'sex_qualifier_label'])
    gene_to_gene_extra_fields = ','.join(['object_taxon', 'object_taxon_label'])

    golr_params = {
        'q': '*:*',
        'wt': 'csv',
        'csv.encapsulator': '"',
        'csv.separator': '\t',
        'csv.header': 'true',
        'csv.mv.separator': '|',
        'fl': default_fields
    }

    for filter in filters:
        if filter == 'category:"biolink:DiseaseToPhenotypicFeatureAssociation"':
            golr_params['fl'] += ',' + disease_to_phenotype_extra_fields
        elif 'GeneToGene' in filter:
            golr_params['fl'] += ',' + gene_to_gene_extra_fields

    count_params = {
        'wt': 'json',
        'rows': 0,
        'q': '*:*',
        'fq': filters,
    }

    sesh = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=10, pool_connections=100, pool_maxsize=100)
    sesh.mount('https://', adapter)
    sesh.mount('http://', adapter)
    solr_request = sesh.get(solr, params=count_params)

    facet_response = None
    retries = 10
    resultCount = 0
    for ret in range(retries):
        if facet_response:
            break

        try:
            facet_response = solr_request.json()
            resultCount = facet_response['response']['numFound']

            if resultCount == 0:
                logger.warning("No results found for {}"
                               " with filters {}".format(tsv_fh.name, filters))
        except decoder.JSONDecodeError:
            logger.warning("JSONDecodeError for {}"
                           " with filters {}".format(tsv_fh.name, filters))
            logger.warning("solr content: {}".format(solr_request.text))
            time.sleep(500)

    if not facet_response:
        logger.error("Could not fetch solr docs with for params %s", filters)
        exit(1)

    golr_params['rows'] = 5000
    golr_params['start'] = 0
    golr_params['fq'] = filters

    first_res = True

    while golr_params['start'] < resultCount:
        if first_res:
            golr_params['csv.header'] = 'true'
            first_res = False
        else:
            golr_params['csv.header'] = 'false'

        solr_response = fetch_solr_doc(sesh, solr, golr_params)

        tsv_fh.write(solr_response)
        golr_params['start'] += golr_params['rows']

    sesh.close()


def generate_jsonl(fh, solr, filters):

    #jsonl_writer = jsonlines.open(fh)

    golr_params = {
        'q': '*:*',
        'wt': 'json',
        'fl': '*',
        'fq': filters,
        'start': 0,
        'rows': 5000
    }

    count_params = {
        'wt': 'json',
        'rows': 0,
        'q': '*:*',
        'fq': filters,
    }

    sesh = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=10, pool_connections=100, pool_maxsize=100)
    sesh.mount('https://', adapter)
    sesh.mount('http://', adapter)
    solr_request = sesh.get(solr, params=count_params)

    facet_response = None
    retries = 10
    resultCount = 0
    for ret in range(retries):
        if facet_response:
            break

        try:
            facet_response = solr_request.json()
            resultCount = facet_response['response']['numFound']

            if resultCount == 0:
                logger.warning("No results found for {}"
                               " with filters {}".format(fh.name, filters))
        except decoder.JSONDecodeError:
            logger.warning("JSONDecodeError for {}"
                           " with filters {}".format(fh.name, filters))
            logger.warning("solr content: {}".format(solr_request.text))
            time.sleep(500)

    if not facet_response:
        logger.error("Could not fetch solr docs with for params %s", filters)
        exit(1)

    while golr_params['start'] < resultCount:
        solr_response = fetch_solr_doc(sesh, solr, golr_params)
        docs = json.loads(solr_response)['response']['docs']
        for doc in docs:
            fh.write(f"{json.dumps(doc)}\n")
        golr_params['start'] += golr_params['rows']

    sesh.close()


def fetch_solr_doc(session, solr, params, retries=10):
    solr_response = None

    for ret in range(retries):
        if solr_response:
            break
        try:
            solr_request = session.get(solr, params=params, stream=False)
            solr_response = solr_request.text
        except ChunkedEncodingError:
            logger.warning("ChunkedEncodingError for params %s", params)
            time.sleep(300)

    if not solr_response:
        logger.error("Could not fetch solr docs with for params %s", params)
        exit(1)

    return solr_response


def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

