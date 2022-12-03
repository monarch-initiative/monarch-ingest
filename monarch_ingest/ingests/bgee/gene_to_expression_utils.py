import uuid
import pandas as pd
from typing import Dict, List, Union
from koza.app import KozaApp
from biolink.pydanticmodel import GeneToExpressionSiteAssociation


def filter_group_by_rank(rows: list, col: str, largest_n: int = 0, smallest_n: int = 0) -> List[Dict]:
    df = pd.DataFrame(rows)
    largest_df = df.nlargest(largest_n, col, keep="first")
    smallest_df = df.nsmallest(smallest_n, col, keep="first")
    return pd.concat([largest_df, smallest_df]).to_dict('records')


def write_group(rows: List, koza_app: KozaApp):
    for row in rows:
        association = GeneToExpressionSiteAssociation(
            id="uuid:" + str(uuid.uuid1()),
            subject="ENSEMBL:" + row['Gene ID'],
            predicate='biolink:expressed_in',
            object=row['Anatomical entity ID'],
            aggregator_knowledge_source=["infores:monarchinitiative", "infores:bgee"])

        koza_app.write(association)


def get_row_group(koza_app: KozaApp, col: str = 'Gene ID') -> Union[List, None]:
    if not hasattr(koza_app, 'previous_row'):
        koza_app.previous_row = koza_app.get_row()

    if koza_app.previous_row is None:
        return None

    rows = [koza_app.previous_row]
    current_row = koza_app.get_row()

    while rows[0][col] == current_row[col]:
        rows.append(current_row)
        current_row = koza_app.get_row()

    koza_app.previous_row = current_row
    return rows


def process_koza_source(koza_app: KozaApp):
    while(row_group := get_row_group(koza_app)) is not None:
        rank_filtered_rows = filter_group_by_rank(row_group, col='Expression rank', smallest_n=10)
        write_group(rank_filtered_rows, koza_app)
