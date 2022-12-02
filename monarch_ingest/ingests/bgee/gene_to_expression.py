import uuid
import pandas as pd
from typing import Dict, List
from koza.cli_runner import *
from biolink.pydanticmodel import GeneToExpressionSiteAssociation

# The source name is used for reading and writing
source_name = "bgee_gene_to_expression"
koza_app = get_koza_app(source_name)


def filter_group_by_rank(rows: list, col: str, largest_n: int = 0, smallest_n: int = 0) -> List[Dict]:
    df = pd.DataFrame(rows)
    largest_df = df.nlargest(largest_n, col, keep="first")
    smallest_df = df.nsmallest(smallest_n, col, keep="first")
    return pd.concat([largest_df, smallest_df]).to_dict('records')


def write_group(rows: List):
    for row in rows:
        association = GeneToExpressionSiteAssociation(
            id="uuid:" + str(uuid.uuid1()),
            subject="ENSEMBL:" + row['Gene ID'],
            predicate='biolink:expressed_in',
            object=row['Anatomical entity ID'],
            aggregator_knowledge_source=["infores:monarchinitiative", "infores:bgee"])

        koza_app.write(association)


group_rows = []
seen_ids = set()
while (koza_row := koza_app.get_row()) is not None:
    if len(group_rows) == 0:
        if koza_row['Gene ID'] in seen_ids:
            message = "Data not sorted by `Gene ID`: cannot group rows for rank-based filtering"
            raise ValueError(message)
        group_rows.append(koza_row)
        seen_ids.add(koza_row['Gene ID'])
    elif koza_row['Gene ID'] == group_rows[0]['Gene ID']:
        group_rows.append(koza_row)
    else:
        rank_filtered_rows = filter_group_by_rank(group_rows, col='Expression rank', smallest_n=10)
        write_group(rank_filtered_rows)
        group_rows = []

rank_filtered_rows = filter_group_by_rank(group_rows)
write_group(rank_filtered_rows)
