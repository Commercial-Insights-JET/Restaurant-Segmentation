"""
This is a boilerplate pipeline 'preprocessing'
generated using Kedro 0.18.12
"""

from kedro.pipeline import Pipeline, pipeline, node
from .nodes import combine_menus, engineer_menu_data, engineer_restaurant_data


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=combine_menus,
                inputs=[
                    "latest_menus_1",
                    "latest_menus_2",
                    "latest_menus_3",
                    "latest_menus_4",
                ],
                outputs="menus_combined",
                name="retired_combine_partitioned_menus",
                tags="retired",
            ),
            node(
                func=engineer_menu_data,
                inputs="menus_combined",
                outputs="menus_data",
                name="retired_engineer_menu_data",
                tags="retired",
            ),
            node(
                func=engineer_restaurant_data,
                inputs=["jet_restaurants","params:prospects_data_false", "menus_data"],
                outputs="retired_restaurants_data",
                name="retired_engineer_restaurant_data",
                tags="retired",
            ),
            node(
                func=engineer_restaurant_data,
                inputs=["jet_restaurants","params:prospects_data_false"],
                outputs="restaurants_data",
                name="engineer_restaurant_data",
                tags="train_models",
            ),
            node(
                func=engineer_restaurant_data,
                inputs=["prospect_restaurants","params:prospects_data_true"],
                outputs="prospects_data",
                name="engineer_prospects_data",
                tags="predict",
            ),
        ],
        tags="pipeline_1_preprocessing"
    )        