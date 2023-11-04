"""
This is a boilerplate pipeline 'model_tpot'
generated using Kedro 0.18.12
"""

from kedro.pipeline import Pipeline, node, pipeline

from .nodes import tpot_run


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=tpot_run,
                inputs=["data_17_x", "data_y", "params:model_options"],
                outputs="tpot_output",
                name="tpot_selector",
            ),
        ], tags="pipeline_6_model_tpot"
    )
