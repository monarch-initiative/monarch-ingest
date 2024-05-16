
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
from typing import List

import yaml
import gzip
import time
import re
import duckdb

import requests
from requests.exceptions import ChunkedEncodingError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OutputType(str, Enum):
    tsv = 'tsv'
    jsonl = 'jsonl'


OUTPUT_TYPES = set(OutputType._member_names_)

DEFAULT_FIELDS = [
            'subject',
            'subject_label',
            'subject_taxon',
            'subject_taxon_label',
            'negated',
            'predicate',
            'object',
            'object_label',
            'qualifiers',
            'publications',
            'has_evidence',
            'primary_knowledge_source',
            'aggregator_knowledge_source',
        ]

DISEASE_TO_PHENOTYPE_APPENDS = [
            'onset_qualifier',
            'onset_qualifier_label',
            'frequency_qualifier',
            'frequency_qualifier_label',
            'sex_qualifier',
            'sex_qualifier_label'
    ]

GENE_TO_GENE_APPENDS = [
            'object_taxon',
            'object_taxon_label'
    ]

def export(config_file: str = "./src/monarch_ingest/data-dump-config.yaml",
           output_dir: str = "./output/tsv/",
           output_format: OutputType = OutputType.tsv,
           solr_url: str = "http://localhost:8983/solr/association/select"):

    if output_format not in OUTPUT_TYPES:
        raise ValueError(f"output format not supported, supported formats are {OUTPUT_TYPES}")
    database = duckdb.connect('output/monarch-kg.duckdb')
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

    for association_category in get_association_categories(database):
        category_name = camel_to_snake(re.sub(r'biolink:', '', association_category))
        # quote the facet value because of the biolink: prefix
        association_category = f'"{association_category}"'
        print(association_category)
        file = f"{category_name}.all.{output_format.value}.gz"
        dump_file = str(dump_dir / file)
        filters = ['category:{}'.format(association_category)]
        export_annotations(database=database,
                                          fields=get_fields(association_category),
                                          category=association_category,
                                          output_file=dump_file,
                                          )
        logger.info(f"finished writing {file}")

    # Fetch associations configured in config_file
    conf_fh = open(config_file, 'r')
    file_filter_map = yaml.safe_load(conf_fh)

    for directory, file_maps in file_filter_map.items():
        dump_dir = dir_path / directory
        dump_dir.mkdir(parents=True, exist_ok=True)

        for file, filters in file_maps.items():
            dump_file = str(dump_dir / file)
            exploded = filters.get('exploded', False)
            export_annotations(database=database,
                               fields=get_fields(filters.get('category')),
                               output_file=dump_file,
                               category=filters.get('category'),
                               subject_taxon=filters.get('taxon', None))

            if exploded:
                exploded_file = dump_file.replace(f'.{output_format.value}.gz',  f'.exploded.{output_format.value}.gz')
                export_exploded_annotations(
                    database=database,
                    category=filters.get('category'),
                    subject_taxon=filters.get('taxon', None),
                    fields=get_fields(filters.get('category')),
                    output_file=exploded_file
                )




def get_fields(category: str) -> List[str]:
    fields = DEFAULT_FIELDS

    if 'category:"biolink:DiseaseToPhenotypicFeatureAssociation"' in category:
        fields += DISEASE_TO_PHENOTYPE_APPENDS
    if 'GeneToGene' in category:
        fields += GENE_TO_GENE_APPENDS

    return fields

def export_annotations(database, fields: List[str], output_file: str, category: str, subject_taxon=None ):
    taxon_filter = "subject_taxon = '{subject_taxon}' " if subject_taxon else ""
    sql = f""" 
    COPY (
        SELECT {','.join(fields)} 
        FROM denormalized_edges 
        WHERE category = '{category}' {taxon_filter}
    ) to '{output_file}' (header, delimiter '\t')
    """
    # database.execute(sql)

def export_exploded_annotations(database,
                                                         fields: List[str],
                                                         output_file: str,
                                                         category :str,
                                                         subject_taxon :str = None):

    taxon_filter = f"AND subject_taxon = '{subject_taxon}'" if subject_taxon else ""

    sql = f"""
        WITH cte AS (
          SELECT
            {','.join(fields)},
            unnest(string_split(object_closure,'|')) as object_ancestor,    
            CASE WHEN object = object_ancestor THEN TRUE ELSE FALSE END as direct
          FROM denormalized_edges
          WHERE category = '{category}' {taxon_filter}
        )
        SELECT
          cte.* REPLACE (cte.object_ancestor as object, nodes.name as object_label)  
        FROM cte
        LEFT OUTER JOIN nodes ON cte.object = nodes.id
    """
    print(sql)
    print(output_file)
    database.execute(f"copy ({sql}) to '{output_file}' (header, delimiter '\t')")

def get_association_categories(database) -> List[str]:
    sql = """
    SELECT DISTINCT category
    FROM denormalized_edges
    """
    # return as list of strings, extracting only column from tuple
    return [row[0] for row in database.execute(sql).fetchall()]



def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

