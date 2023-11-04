"""
This is a boilerplate pipeline 'predict'
generated using Kedro 0.18.12
"""
import pandas as pd


def predict_with_model(model_pkl, to_predict):
    result = model_pkl.predict(to_predict)
    predicted = pd.DataFrame()
    predicted["score"] = result
    predicted["score"] = predicted["score"].round(3)
    return predicted


def combine_predictions(context, output_1, output_2, output_3, output_4):
    combined = pd.concat([output_1, output_2, output_3, output_4], axis=1)
    combined.columns = ["xgb_17", "xgb_full", "kmeans_3", "kmeans_10"]
    combined = pd.concat([context,combined], axis=1)
    key_columns = ['global_place_id','restaurant_name','restaurant_key','restaurant_id_local','model_training_data']
    non_key_columns = [col for col in list(combined) if col not in key_columns]
    combined = combined[key_columns+non_key_columns]
    return combined
