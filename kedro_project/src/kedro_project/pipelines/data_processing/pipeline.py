# src/kedro_project/pipelines/data_engineering/pipeline.py

from kedro.pipeline import Pipeline, node
from .nodes import load_to_postgresql

def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                func=load_to_postgresql,
                inputs=["raw_telegram_data", "params:table_names.raw_telegram_data", "credentials.postgresql"],
                outputs=None,
                name="load_raw_telegram_data_to_postgresql"
            ),
            node(
                func=load_to_postgresql,
                inputs=["raw_google_play_reviews", "params:table_names.playstore_reviews", "credentials.postgresql"],
                outputs=None,
                name="load_raw_google_play_reviews_to_postgresql"
            ),
            node(
                func=load_to_postgresql,
                inputs=["raw_google_play_downloads", "params:table_names.google_play_downloads", "credentials.postgresql"],
                outputs=None,
                name="load_raw_google_play_downloads_to_postgresql"
            ),
            node(
                func=load_to_postgresql,
                inputs=["raw_telegram_subscription_growth", "params:table_names.telegram_subscription_growth", "credentials.postgresql"],
                outputs=None,
                name="load_raw_telegram_subscription_growth_to_postgresql"
            )
        ]
    )
