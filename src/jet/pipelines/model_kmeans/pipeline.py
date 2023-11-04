"""
This is a boilerplate pipeline 'model_kmeans'
generated using Kedro 0.18.12
"""

from kedro.pipeline import Pipeline, pipeline, node
from .nodes import create_kmeans_3, create_kmeans_10, predict_kmeans, kmeans_plot, get_top_features


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=create_kmeans_3,
                inputs="predict_features_data",
                outputs="kmeans_3_model",
                name="kmeans_3_clusters",
            ),
            node(
                func=predict_kmeans,
                inputs=["kmeans_3_model", "predict_features_data"],
                outputs="kmeans_3_output",
                name="kmeans_3_clusters_predict",
            ),
            node(
                func=kmeans_plot,
                inputs=["combined_predictions", "params:kmeans_3_model_name","predict_features_data", "combined_predictions", "kmeans_3_output", "kmeans_3_model"],
                outputs="output_plot_kmeans_3",
                name="kmeans_3_visualise",
            ),
            node(
                func=get_top_features,
                inputs=["predict_features_data", "combined_predictions", "kmeans_3_output", "kmeans_3_model"],
                outputs="output_top_features_kmeans_3",
                name="kmeans_3_top_features",
            ),
            node(
                func=create_kmeans_10,
                inputs="predict_features_data",
                outputs="kmeans_10_model",
                name="kmeans_10_clusters",
            ),
            node(
                func=predict_kmeans,
                inputs=["kmeans_10_model", "predict_features_data"],
                outputs="kmeans_10_output",
                name="kmeans_10_clusters_predict",
            ),
            node(
                func=kmeans_plot,
                inputs=["combined_predictions", "params:kmeans_10_model_name","predict_features_data", "combined_predictions", "kmeans_10_output", "kmeans_10_model"],
                outputs="output_plot_kmeans_10",
                name="kmeans_10_visualise",
            ),
            node(
                func=get_top_features,
                inputs=["predict_features_data", "combined_predictions", "kmeans_10_output", "kmeans_10_model"],
                outputs="output_top_features_kmeans_10",
                name="kmeans_10_top_features",
            ),
        ],
        tags=["model_kmeans","pipeline_5_model_kmeans","predict"],
    )
