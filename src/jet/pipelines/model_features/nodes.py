"""
This is a boilerplate pipeline 'model_features'
generated using Kedro 0.18.12
"""

from typing import Tuple
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def col_tidy(df):
    tidy_col_list = []
    for c in df.columns:
        c = c.lower()
        c = c.replace(" ", "_")
        tidy_col_list.append(c)
    df.columns = tidy_col_list
    return df


def get_data_with_target(data_df, scorecard_df):
    data_df = data_df.merge(
        scorecard_df[["restaurant_key", "score", "score_rank"]],
        how="left",
        on="restaurant_key",
    )
    return data_df


def set_feature_type():
    not_using = [
        "restaurant_id_local",
        "global_place_id",
        "miod_10_orders",
        "miod_9_orders",
        "miod_8_orders",
        "miod_7_orders",
        "miod_6_orders",
        "miod_5_orders",
        "miod_4_orders",
        "miod_3_orders",
        "miod_2_orders",
        "miod_1_orders",
        "miod__orders",
        "miod_10_customers",
        "miod_9_customers",
        "miod_8_customers",
        "miod_7_customers",
        "miod_6_customers",
        "miod_5_customers",
        "miod_4_customers",
        "miod_3_customers",
        "miod_2_customers",
        "miod_1_customers",
        "miod__customers",
        "hva_8_orders",
        "hva_7_orders",
        "hva_6_orders",
        "hva_5_orders",
        "hva_4_orders",
        "hva_3_orders",
        "hva_2_orders",
        "hva_1_orders",
        "hva__orders",
        "hva_8_customers",
        "hva_7_customers",
        "hva_6_customers",
        "hva_5_customers",
        "hva_4_customers",
        "hva_3_customers",
        "hva_2_customers",
        "hva_1_customers",
        "hva__customers",
        "restaurant_area",
        "cuisine",
        "model_training_data",
        "jet_active",
        "rest_key",
        "Delivery_Package__c",
        "grocery_flag",
        "cuisine_primary",
        "cuisine_secondary",
        "district_city",
        "restaurant_district",
        "restaurant_postcode",
        "rest_group",
        "chain_flag",
        "jet_rating",
        "jet_reviews",
        "google_primary_cuisine",
        "google_secondary_cuisine",
        "google_cuisine_types",
        "google_dish_types",
        "avg_main_price",
        "total_rating_with_jet",
    ]

    cols_target = ["score", "score_rank"]
    cols_descriptive = ["restaurant_key", "restaurant_name"]
    cols_nominal = ["FSA_Rating", "rural_classification", "restaurant_hva"]
    cols_boolean = [
        "goo_active",
        "roo_active",
        "uber_active",
        "ta_active",
        "google_open_status",
        "url",
    ]
    cols_numerical = [
        "restaurant_miod",
        "population_density",
        "goo_rating",
        "goo_reviews",
        "roo_rating",
        "roo_reviews",
        "uber_rating",
        "uber_reviews",
        "ta_rating",
        "ta_reviews",
        "total_rating",
        "total_reviews",
        "district_num",
    ]
    cols_nested = ['google_location_types']

    return (
        cols_descriptive,
        cols_nominal,
        cols_boolean,
        cols_numerical,
        cols_nested,
        cols_target,
        not_using,
    )


def check_feature_missing(
    data_df,
    cols_descriptive,
    cols_nominal,
    cols_boolean,
    cols_numerical,
    cols_nested,
    cols_target,
    not_using,
):
    missed_cols = [
        col
        for col in list(data_df)
        if col
        not in cols_descriptive
        + cols_nominal
        + cols_boolean
        + cols_numerical
        + cols_nested
        + cols_target
        + not_using
    ]

    print(f"missed cols: {missed_cols}")
    return


def get_valid_features(
    data_df,
    cols_descriptive,
    cols_nominal,
    cols_boolean,
    cols_numerical,
    cols_nested,
):
    valid_features_df = data_df[
        cols_descriptive + cols_nominal + cols_boolean + cols_numerical + cols_nested
    ]
    return valid_features_df


def treat_features_manual(data_df, cols_boolean):
    ### has 'url'
    data_df["url_has"] = data_df["url"].apply(lambda x: 1 if x == x else 0)
    data_df = data_df.drop(columns=["url"])
    cols_boolean.remove("url")
    cols_boolean = cols_boolean + ["url_has"]

    ### todo: active on google, uber ears, deliveroo or trip advisor
    # data['goo_roo_uber_ta_active'] = data['goo_active']=1

    ### is open on google
    data_df["google_open_status_isopen"] = data_df["google_open_status"].apply(
        lambda x: 1 if x == "OPEN" else 0
    )
    data_df = data_df.drop(columns=["google_open_status"])
    cols_boolean.remove("google_open_status")
    cols_boolean = cols_boolean + ["google_open_status_isopen"]

    return data_df, cols_boolean


def treat_features_nested(data_df, cols_nested):
    for col in cols_nested:
        cols_encoded = data_df[col].str.split(",")
        cols_encoded = cols_encoded.fillna("")
        cols_encoded = cols_encoded.apply(
            lambda x: [w.lstrip().replace("-", " ").replace(" ", "_") for w in x]
        )
        cols_encoded = (
            pd.get_dummies(cols_encoded.explode(), prefix=col, prefix_sep="_")
            .groupby(level=0)
            .sum()
        )
        data_df = data_df.drop(columns=[col])
        data_df = data_df.join(cols_encoded)
    return data_df, cols_nested


def treat_features_nominal(data_df, cols_nominal, cols_boolean):
    for col in cols_nominal:
        cols_encoded = pd.get_dummies(data_df[col], prefix=col, prefix_sep="_")
        data_df = data_df.drop(columns=[col])
        data_df = data_df.join(cols_encoded)
        cols_boolean = cols_boolean + [
            ce.replace(" ", "_").lower() for ce in list(cols_encoded)
        ]
    return data_df, cols_nominal, cols_boolean


def scale_features(data_df, exclude_cols_lists, trained_scaler=None):
    exclude_cols = [col for sublist in exclude_cols_lists for col in sublist]
    data_features = data_df.drop(columns=exclude_cols)
    if trained_scaler is None:
        scaler = MinMaxScaler().fit(data_features.values)
    else:
        scaler = trained_scaler
    data_features = pd.DataFrame(
        scaler.transform(data_features.values),
        columns=data_features.columns,
        index=data_features.index,
    )
    scaled_df = pd.concat([data_features, data_df[exclude_cols]], axis=1)
    return scaled_df, scaler


def create_features(data_df, trained_scaler=None, trained_df_columns=None):
    ### Check feature setup
    (
        cols_descriptive,
        cols_nominal,
        cols_boolean,
        cols_numerical,
        cols_nested,
        cols_target,
        not_using,
    ) = set_feature_type()

    ### Select relevant features only
    data_valid_features = get_valid_features(
        data_df,
        cols_descriptive,
        cols_nominal,
        cols_boolean,
        cols_numerical,
        cols_nested,
    )

    ### Treating all features
    data_valid_features, cols_boolean = treat_features_manual(
        data_valid_features, cols_boolean
    )
    data_valid_features, cols_nested = treat_features_nested(
        data_valid_features, cols_nested
    )
    (
        data_valid_features,
        cols_nominal,
        cols_boolean,
    ) = treat_features_nominal(data_valid_features, cols_nominal, cols_boolean)
    data_valid_features = col_tidy(data_valid_features)
    
    ### If this is feature creation for prediction
    if trained_df_columns is not None:
        ### then create any missing columns to match training dataset and fill with 0
        data_valid_features = fill_missing_features(
            trained_df_columns, data_valid_features
        )
        ### and remove any extra columns not also present in the training dataset
        data_valid_features = remove_extra_features(
            trained_df_columns, data_valid_features
        )

    ### Fill any other missing data with 0
    data_valid_features = data_valid_features.fillna(0)

    ### Create new scaler, or scale new data to existing scale in training set
    data_valid_features, new_trained_scaler = scale_features(
        data_valid_features, [cols_descriptive], trained_scaler
    )

    ### Retain scaled dataset and new scaler only. Does not re-save an existing scaler
    if trained_scaler is None:
        return data_valid_features, new_trained_scaler
    if trained_scaler is not None:
        return data_valid_features


def add_target_to_features(data_df, scorecard_df):
    ### Add scores (target) to features
    data_with_target = get_data_with_target(data_df, scorecard_df)
    return data_with_target

def get_target(scorecard_df):
    data_y = scorecard_df["score"]
    return data_y

def check_data_missing(data_df):
    ### Check feature setup and identify missing ones
    (
        cols_descriptive,
        cols_nominal,
        cols_boolean,
        cols_numerical,
        cols_nested,
        cols_target,
        not_using,
    ) = set_feature_type()
    check_feature_missing(
        data_df,
        cols_descriptive,
        cols_nominal,
        cols_boolean,
        cols_numerical,
        cols_nested,
        cols_target,
        not_using,
    )
    return None


def select_features_17(data: pd.DataFrame) -> Tuple:
    features = [
        "goo_rating",
        "uber_rating",
        "roo_rating",
        "ta_rating",
        "total_reviews",
        "url_has",
        "restaurant_miod",
        "district_num",
        "population_density",
        "rural_classification_rural_town_and_fringe",
        "restaurant_hva_2._wealthy",
        "restaurant_hva_3._younger_urban_spender",
        "restaurant_hva_7._older_suburban_spender",
        "google_open_status_isopen",
    ]
    data_x = data[features]
    return data_x


def select_features_full(data, trained_columns=None):
    ### if is predictions - reorder columns to match training data
    if trained_columns is None:
        data_x = data
        data_x = data_x.drop(columns=["restaurant_key", "restaurant_name"])
    else:
        trained_columns.remove('restaurant_key')
        trained_columns.remove('restaurant_name')
        data_x = data[trained_columns]
    
    return data_x


def fill_missing_features(trained_df_columns, predict_features_df):
    predict_schema = list(predict_features_df)
    for column in trained_df_columns:
        if column not in predict_schema:
            predict_features_df[column] = 0
    return predict_features_df

def remove_extra_features(trained_df_columns, predict_features_df):
    predict_schema = list(predict_features_df)
    for column in predict_schema:
        if column not in trained_df_columns:
            predict_features_df = predict_features_df.drop(columns=[column])
    return predict_features_df

def get_trained_columns(trained_df):
    return list(trained_df)

def combine_dataset_predicting(trained_features_df, predict_features_df, params_context, scorecard=None):
    if predict_features_df is not None and len(predict_features_df)>0:
        combined = pd.concat([predict_features_df,trained_features_df],axis=0)
    else:
        combined = trained_features_df

    if params_context == False:
        combined = combined.drop(columns=["restaurant_key", "restaurant_name"])
    else:
        scorecard = scorecard[['restaurant_key','score']].drop_duplicates()
        mapping = dict(scorecard.values)
        combined['score'] = combined.restaurant_key.map(mapping)
    return combined