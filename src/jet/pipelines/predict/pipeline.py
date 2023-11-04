"""
This is a boilerplate pipeline 'predict'
generated using Kedro 0.18.12
"""

from kedro.pipeline import Pipeline, pipeline, node
from .nodes import predict_with_model, combine_predictions


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=predict_with_model,
                inputs=["model_xgb_17", "predict_17_x"],
                outputs="model_predicted_xgb",
                name="predict_with_model_xgb_17",
            ),
            node(
                func=predict_with_model,
                inputs=["model_xgb_full", "predict_full_x"],
                outputs="model_predicted_xgb_full",
                name="predict_with_model_xgb_full",
            ),
            node(
                func=combine_predictions,
                inputs=[
                    "predict_features_data_context",
                    "model_predicted_xgb",
                    "model_predicted_xgb_full",
                    "kmeans_3_output",
                    "kmeans_10_output",
                ],
                outputs="combined_predictions",
                name="combine_predictions",
            ),
            
        ],
        tags=["predict","pipeline_7_predict"]
    )
