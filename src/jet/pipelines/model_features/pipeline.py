"""
This is a boilerplate pipeline 'model_features'
generated using Kedro 0.18.12
"""

from kedro.pipeline import Pipeline, pipeline, node
from .nodes import (
    create_features,
    add_target_to_features,
    select_features_17,
    select_features_full,
    get_target,
    get_trained_columns,
    combine_dataset_predicting,
)


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=create_features,
                inputs="qualified_restaurants_data",
                outputs=["train_features_data", "trained_scaler"],
                name="create_train_features",
                tags="train_models",
            ),
            node(
                func=select_features_17,
                inputs="train_features_data",
                outputs="data_17_x",
                name="extract_features_17",
                tags=["model_xgb_17","train_models"],
            ),
            node(
                func=select_features_full,
                inputs="train_features_data",
                outputs="data_full_x",
                name="extract_features_full",
                tags=["model_xgb_full", "train_models"],
            ),
            node(
                func=get_target,
                inputs="scorecard_data",
                outputs="data_y",
                name="extract_target",
                tags="train_models",
            ),
            node(
                func=add_target_to_features,
                inputs=["train_features_data", "scorecard_data"],
                outputs="featureswithtarget_data",
                name="add_target_to_features",
                tags="train_models",
            ),
            node(
                func=get_trained_columns,
                inputs=["train_features_data"],
                outputs="trained_columns_list",
                name="list_trained_predict_features",
                tags="predict",
            ),
            node(
                func=create_features,
                inputs=["prospects_data", "trained_scaler", "trained_columns_list"],
                outputs="prospects_features_data",
                name="create_prospect_features",
                tags="predict",
            ),
            node(
                func=combine_dataset_predicting,
                inputs=["train_features_data","prospects_features_data","params:context_false"],
                outputs="predict_features_data",
                name="combine_prospect_and_train_for_prediction",
                tags=["predict"],
            ),
            node(
                func=select_features_17,
                inputs="predict_features_data",
                outputs="predict_17_x",
                name="retain_predict_features_17",
                tags="predict",
            ),
            node(
                func=select_features_full,
                inputs=["predict_features_data","trained_columns_list"],
                outputs="predict_full_x",
                name="retain_predict_features_full",
                tags="predict",
            ),
            node(
                func=combine_dataset_predicting,
                inputs=["qualified_restaurants_data","prospects_data","params:context_true", "scorecard_data"],
                outputs="predict_features_data_context",
                name="combine_prospect_and_train_for_prediction_context",
                tags=["predict"],
            ),
        ], tags=['pipeline_3_model_features']
    )
