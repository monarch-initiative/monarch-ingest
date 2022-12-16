import uuid
import pandas as pd
from typing import Dict, List, Union
from koza.app import KozaApp
from biolink.pydanticmodel import GeneToExpressionSiteAssociation


def filter_group_by_rank(rows: List, col: str, largest_n: int = 0, smallest_n: int = 0) -> List[Dict]:
    """Function to filter a group of Koza rows by values largest or smallest values in column:

        Get the top and/or bottom n rows ranked based on column:

        Args:
            rows (List): The Koza object to read rows from.
            col (str): The column to perform ranking and filtering.
            largest_n (int): The number of rows to return from the largest ranking.
            smallest_n (int): The number of rows to return from the smallest ranking.


        Returns:
            List[Dict]: Returns a list of n rows in Koza dict format sorted by rank in column.
    """
    df = pd.DataFrame(rows)
    largest_df = df.nlargest(largest_n, col, keep="first")
    smallest_df = df.nsmallest(smallest_n, col, keep="first")
    return pd.concat([largest_df, smallest_df]).to_dict('records')


def write_group(rows: List, koza_app: KozaApp):
    """Function to write a group of Koza rows to KozaApp object output:

        Write list of rows in Koza format to KozaApp output:

        Args:
            rows (List): A list of rows to output to KozaApp.
            koza_app (KozaApp): The KozaApp to use for output of rows.
    """
    for row in rows:
        association = GeneToExpressionSiteAssociation(
            id="uuid:" + str(uuid.uuid1()),
            subject="ENSEMBL:" + row['Gene ID'],
            predicate='biolink:expressed_in',
            object=row['Anatomical entity ID'],
            aggregator_knowledge_source=["infores:monarchinitiative", "infores:bgee"])

        koza_app.write(association)


def get_row_group(koza_app: KozaApp, col: str = 'Gene ID') -> Union[List, None]:
    """Function to read a group of Koza rows from a KozaApp:

        Get a group of rows from KozaApp grouped on column:

        Args:
            koza_app (KozaApp): The Koza object to read rows from.
            col (str): The column to group rows based on.


        Returns:
            List/None: Returns a list of rows in Koza dict format grouped by column.
    """
    if not hasattr(koza_app, 'previous_row'):
        koza_app.previous_row = koza_app.get_row()
    elif koza_app.previous_row is None:
        return None

    rows = [koza_app.previous_row]
    current_row = koza_app.get_row()

    while rows[0][col] == current_row[col]:
        rows.append(current_row)
        current_row = koza_app.get_row()

    koza_app.previous_row = current_row
    return rows


def process_koza_source(koza_app: KozaApp):
    """Function to filter a group of Koza rows by values largest or smallest values in column:

        Get the top and/or bottom n rows ranked based on column:

        Args:
            koza_app (KozaApp): The Koza object to process for ingest.
    """
    while(row_group := get_row_group(koza_app)) is not None:
        rank_filtered_rows = filter_group_by_rank(row_group, col='Expression rank', smallest_n=10)
        write_group(rank_filtered_rows, koza_app)
