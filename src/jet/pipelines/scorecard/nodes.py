"""
This is a boilerplate pipeline 'scorecard'
generated using Kedro 0.18.12
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import logging

def qualify_data(restaurants_data, parameters: dict):
    chain_indie = []
    if parameters["incl_indies"] == 1:
        chain_indie.append(0)

    if parameters["incl_chains"] == 1:
        chain_indie.append(1)

    restaurants_data = restaurants_data[
        (restaurants_data["in_operation_flag"] == 1)
        & (restaurants_data["grocery_flag"] == 0)
        & (restaurants_data["chain_flag"].isin(chain_indie))
        & (restaurants_data["miod__orders"] >= parameters["min_miod_orders"])
    ]
    return restaurants_data


def convert_miod_long(df_data):
    miod_long = pd.melt(
        df_data,
        id_vars=[
            "restaurant_key",
        ],
        value_vars=[
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
        ],
    )
    miod_long["miod"] = (
        miod_long["variable"].apply(lambda x: x.split("_")[1]).astype(int)
    )
    miod_long["variable"] = miod_long["variable"].apply(lambda x: x.split("_")[2])
    miod_long = (
        miod_long.groupby(["restaurant_key", "miod", "variable"])["value"]
        .sum()
        .reset_index()
    )
    miod_long = pd.pivot(
        miod_long,
        index=["restaurant_key", "miod"],
        columns=["variable"],
        values=["value"],
    ).reset_index()
    miod_long.columns = miod_long.columns.droplevel(0)
    miod_long.columns = ("restaurant_key", "miod", "customers", "orders")
    miod_long = miod_long.merge(
        miod_long.groupby(["restaurant_key"])["orders"]
        .sum()
        .reset_index(name="total_orders"),
        how="left",
        on="restaurant_key",
    )
    miod_long = miod_long.merge(
        miod_long.groupby(["restaurant_key"])["customers"]
        .sum()
        .reset_index(name="total_customers"),
        how="left",
        on="restaurant_key",
    )
    miod_long["pcn_orders"] = round(
        (miod_long["orders"] / miod_long["total_orders"]) * 100, 2
    )
    miod_long["pcn_customers"] = round(
        (miod_long["customers"] / miod_long["total_customers"]) * 100, 2
    )
    miod_long["orders/customer"] = miod_long["orders"] / miod_long["customers"]
    miod_long["pcn_orders_rolling"] = (
        miod_long.groupby(["restaurant_key"])["pcn_orders"].rolling(2).sum().values
    )
    miod_long["bucket"] = miod_long["miod"].apply(
        lambda x: "miod_bottom" if x <= 4 else "miod_mid" if x <= 8 else "miod_top"
    )
    miod_long = miod_long.merge(
        miod_long.groupby(["restaurant_key", "bucket"])["orders"]
        .sum()
        .reset_index(name="bucket_orders"),
        how="left",
        on=["restaurant_key", "bucket"],
    )

    miod_long = miod_long.sort_values(by=["restaurant_key", "miod"])
    return miod_long


def get_miod_buckets(df_miod_long):
    miod_buckets = (
        df_miod_long.groupby(["restaurant_key", "bucket"])["orders", "customers"]
        .sum()
        .reset_index()
    )
    miod_buckets.columns = (
        "restaurant_key",
        "bucket",
        "bucket_orders",
        "bucket_customers",
    )
    miod_buckets["bucket_orders_pcn"] = round(
        (
            miod_buckets["bucket_orders"]
            / miod_buckets.groupby(["restaurant_key"])["bucket_orders"].transform("sum")
        )
        * 100,
        2,
    )
    miod_buckets["bucket_customers_pcn"] = round(
        (
            miod_buckets["bucket_customers"]
            / miod_buckets.groupby(["restaurant_key"])["bucket_customers"].transform(
                "sum"
            )
        )
        * 100,
        2,
    )
    miod_buckets["bucket_repeat_orders"] = round(
        miod_buckets["bucket_orders"] / miod_buckets["bucket_customers"], 2
    ).fillna(0)
    miod_buckets = pd.pivot(
        miod_buckets[miod_buckets["bucket"] == "miod_top"],
        index=["restaurant_key"],
        columns=["bucket"],
    ).reset_index()
    miod_buckets.columns = miod_buckets.columns.get_level_values(0)
    miod_buckets = miod_buckets.add_prefix("miod_top_")
    miod_buckets = miod_buckets.rename(
        columns={"miod_top_restaurant_key": "restaurant_key"}
    )
    return miod_buckets


def get_miod_means(data_df):

    miod_order_cols = ['miod_10_orders', 'miod_9_orders', 'miod_8_orders', 'miod_7_orders', 'miod_6_orders', 'miod_5_orders', 'miod_4_orders', 'miod_3_orders', 'miod_2_orders', 'miod_1_orders']
    data_df['mean_miod_order'] = (data_df[miod_order_cols] * list(range(10, 0, -1))).sum(axis = 1)/data_df['miod__orders']

    miod_customer_cols = ['miod_10_customers', 'miod_9_customers', 'miod_8_customers', 'miod_7_customers', 'miod_6_customers', 'miod_5_customers', 'miod_4_customers', 'miod_3_customers', 'miod_2_customers', 'miod_1_customers']
    data_df['mean_miod_customer'] = (data_df[miod_customer_cols] * list(range(10, 0, -1))).sum(axis = 1)/data_df['miod__customers']

    return data_df[['restaurant_key', 'mean_miod_order', 'mean_miod_customer']].drop_duplicates()

def scale_metrics(data_df, parameters: dict):
    scorecard_scaled_metrics = []
    for col in parameters["scaled_metrics"]:
        new_col = col + "_scaled"
        data_df[new_col] = MinMaxScaler().fit_transform(data_df[[col]])
        scorecard_scaled_metrics.append(new_col)
    return data_df, scorecard_scaled_metrics


def get_scorecard_v1(data_df, parameters: dict):

    data_area = data_df
    miod_long = convert_miod_long(data_area)

    miod_buckets = get_miod_buckets(miod_long)
    data_area = data_area.merge(miod_buckets, how="left", on="restaurant_key")

    miod_means = get_miod_means(data_df)
    data_area = data_area.merge(miod_means, how = 'left', on = 'restaurant_key')

    scorecard_agg_cols = []

    for col in parameters["scorecard_metrics"]:
        data_area.loc[data_area[col].isin([0, np.NaN, np.inf]), col] = 0

        if col in parameters["scaled_metrics"]:
            scorecard_agg_cols.append(col + "_scaled")
        else:
            scorecard_agg_cols.append(col)

    data_area, scorecard_scaled_metrics = scale_metrics(data_area, parameters)
    scorecard_cols = [
        "restaurant_key",
        "restaurant_name",
        "cuisine",
        "restaurant_district",
        "miod__customers",
        "avg_main_price",
        "restaurant_miod",
        "miod_top_bucket_orders_pcn",
        "miod_top_bucket_customers_pcn",
        "miod_top_bucket_repeat_orders",
        "total_rating_with_jet",
        'mean_miod_order',
        'mean_miod_customer'
    ] + scorecard_scaled_metrics
    scorecard = data_area[scorecard_cols]

    scorecard["score"] = scorecard[scorecard_agg_cols].mean(axis=1)
    scorecard["score_rank"] = pd.qcut(scorecard["score"], q=10, duplicates='drop').cat.codes + 1
    return scorecard
