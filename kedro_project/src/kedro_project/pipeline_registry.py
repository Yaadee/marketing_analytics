# src/kedro_project/pipeline_registry.py

from kedro.pipeline import Pipeline
from kedro_project.pipelines.data_processing import pipeline as de_pipeline

def register_pipelines() -> dict[str, Pipeline]:
    return {
        "__default__": de_pipeline.create_pipeline(),
        "de": de_pipeline.create_pipeline(),
    }
