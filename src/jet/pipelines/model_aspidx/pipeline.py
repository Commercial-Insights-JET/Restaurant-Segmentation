"""
This is a boilerplate pipeline 'model_aspidx'
generated using Kedro 0.18.12
"""


from kedro.pipeline import Pipeline, node, pipeline

from .nodes import (
    train_model_xgb,
    evaluate_model,
    prediction_output,
    visualise_predictions,
)


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=train_model_xgb,
                inputs=["data_17_x", "data_y"],
                outputs="model_xgb_17",
                name="train_XGBRegressor_data_17",
                tags=["model_xgb_17",'train_models'],
            ),
            node(
                func=prediction_output,
                inputs=[
                    "model_xgb_17",
                    "data_17_x",
                    "data_y",
                    "params:model_options",
                ],
                outputs="prediction_output_xgb_17",
                tags=["model_xgb_17",'train_models'],
            ),
            node(
                func=evaluate_model,
                inputs=["data_y", "prediction_output_xgb_17"],
                outputs="algo_metrics_xgb_17",
                name="evaluate_xgb",
                tags=["model_xgb_17",'train_models'],
            ),
            node(
                func=visualise_predictions,
                inputs=["data_y", "prediction_output_xgb_17", "params:model_xgb_17"],
                outputs="output_plot_xgb_17",
                name="visualise_predictions_xgb",
                tags=["model_xgb_17",'train_models'],
            ),
            node(
                func=train_model_xgb,
                inputs=["data_full_x", "data_y"],
                outputs="model_xgb_full",
                name="train_xgb_full",
                tags=["model_xgb_full",'train_models'],
            ),
            node(
                func=prediction_output,
                inputs=[
                    "model_xgb_full",
                    "data_full_x",
                    "data_y",
                    "params:model_options",
                ],
                outputs="prediction_output_xgb_full",
                tags=["model_xgb_full",'train_models'],
            ),
            node(
                func=evaluate_model,
                inputs=["data_y", "prediction_output_xgb_full"],
                outputs="algo_metrics_xgb_full",
                name="evaluate_xgb_full",
                tags=["model_xgb_full",'train_models'],
            ),
            node(
                func=visualise_predictions,
                inputs=[
                    "data_y",
                    "prediction_output_xgb_full",
                    "params:model_xgb_full",
                ],
                outputs="output_plot_xgb_full",
                name="visualise_predictions_xgb_full",
                tags=["model_xgb_full",'train_models'],
            ),
        ], tags="pipeline_4_model_aspidx"
    )