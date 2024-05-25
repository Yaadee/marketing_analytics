# src/kedro_project/pipelines/data_engineering/nodes.py

import pandas as pd
from sqlalchemy import create_engine

def load_to_postgresql(data: pd.DataFrame, table_name: str, credentials: dict) -> None:
    engine = create_engine(credentials['con'])
    data.to_sql(table_name, engine, if_exists='replace', index=False)
