"""
This is a boilerplate pipeline 'scorecard'
generated using Kedro 0.18.12
"""

from kedro.pipeline import Pipeline, pipeline, node
from .nodes import qualify_data, get_scorecard_v1


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=qualify_data,
                inputs=["restaurants_data", "params:scorecard_options"],
                outputs="qualified_restaurants_data",
                name="qualify_data",
                tags="train_models",
            ),
            node(
                func=get_scorecard_v1,
                inputs=["qualified_restaurants_data", "params:scorecard_options"],
                outputs="scorecard_data",
                name="get_scorecard",
                tags="train_models",
            ),
        ], tags="pipeline_2_scorecard"
    )
