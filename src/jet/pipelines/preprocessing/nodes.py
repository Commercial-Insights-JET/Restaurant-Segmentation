"""
This is a boilerplate pipeline 'preprocessing'
generated using Kedro 0.18.12
"""
import pandas as pd
import re
from dateutil.relativedelta import relativedelta


def combine_menus(menus1, menus2, menus3, menus4):
    menus_combined = pd.concat(
        [menus1, menus2, menus3, menus4],
        axis=0,
    )
    return menus_combined


def is_bundle(item_name: str):
    bundle_indicators = [
        "for ",
        "meal",
        "set",
        "persons",
        "deal",
        "family",
        "bundle",
        "feast",
        "combo",
        "dozen",
    ]
    if any(ind.lower() in str(item_name).lower() for ind in bundle_indicators):
        bundle_flag = 1
    else:
        bundle_flag = 0
    return bundle_flag


def engineer_menu_data(menus_combined):
    menu_data = menus_combined.copy()
    menu_data["is_bundle"] = menu_data["item_name"].apply(lambda x: is_bundle(x))
    menu_data["is_bundle"] = menu_data["is_bundle"].astype(int)
    return menu_data

def extract_district_num(x_restaurant_district):
    try:
        district_num = re.sub(r"[^0-9]", "", x_restaurant_district)
    except:
        district_num = None
    return district_num

def engineer_restaurant_geography(restaurants_data):
    ### districts and areas
    restaurants_data["district_num"] = (
        restaurants_data["restaurant_district"]
        .apply(lambda x: extract_district_num(x))
        .astype("Int64")
    )
    restaurants_data["restaurant_area"] = restaurants_data[
        "restaurant_district"
    ].str.replace("\d+", "")
    restaurants_data.loc[
        restaurants_data["restaurant_district"] == "", "restaurant_district"
    ] = None
    return restaurants_data


def engineer_restaurant_cuisine(restaurants_data):
    ### combine primary and secondary cuisine into cuisine
    restaurants_data["cuisine_secondary"] = restaurants_data[
        "cuisine_secondary"
    ].fillna("")
    restaurants_data["cuisine"] = restaurants_data.apply(
        lambda x: [x["cuisine_primary"], x["cuisine_secondary"]], axis=1
    )
    restaurants_data.loc[
        restaurants_data["cuisine_secondary"] == "", "cuisine_secondary"
    ] = None
    return restaurants_data


def engineer_restaurant_operation_dates(restaurants_data,is_prospects_data):

    if is_prospects_data == False:
        restaurants_data["online_date"] = pd.to_datetime(restaurants_data["online_date"])
        max_online_date = restaurants_data["online_date"].max()
        online_date_cutoff = max_online_date - relativedelta(years=1)
        
        restaurants_data.loc[
            restaurants_data["online_date"] <= online_date_cutoff, "in_operation_flag"
        ] = 1

        restaurants_data["model_training_data"] = 1
    else:
        restaurants_data["model_training_data"] = 0
    return restaurants_data

def engineer_restaurant_active_on_jet_flag(restaurants_data):
    restaurants_data['jet_active'] = 0
    restaurants_data.loc[restaurants_data['restaurant_key'].notnull(),'jet_active']=1
    return restaurants_data



def engineer_restaurant_avg_menu_price(restaurants_data, menus_data=None):
    if menus_data is not None:
        # Avg menu price
        avg_menu_prices = (
            menus_data[
                (menus_data["category"] == "main") & (menus_data["is_bundle"] == 0)
            ]
            .groupby(["rest_key"])["item_price"]
            .mean()
            .reset_index()
            .rename(
                columns={"item_price": "avg_main_price", "rest_key": "restaurant_key"}
            )
        )
        restaurants_data = restaurants_data.merge(
            avg_menu_prices, how="left", on="restaurant_key"
        )
    else:
        restaurants_data["avg_main_price"] = None
    return restaurants_data


def engineer_restaurant_total_reviews(restaurants_data):
    ### recalculate Total Reviews to fix error in original data
    restaurants_data["total_rating"] = restaurants_data[
        ["goo_rating", "roo_rating", "uber_rating", "ta_rating"]
    ].mean(axis=1)
    restaurants_data["total_rating_with_jet"] = restaurants_data[
        ["goo_rating", "roo_rating", "uber_rating", "ta_rating","jet_rating"]
    ].mean(axis=1)
    return restaurants_data


def tidy_data(restaurants_data):
    restaurants_data["chain_flag"] = restaurants_data["chain_flag"].astype(int)
    restaurants_data["online_date"] = pd.to_datetime(restaurants_data["online_date"])
    return restaurants_data


def engineer_restaurant_data(jet_restaurants, is_prospects_data, menus_data=None):
    restaurants_data = jet_restaurants.copy()
    restaurants_data = engineer_restaurant_geography(restaurants_data)
    restaurants_data = engineer_restaurant_cuisine(restaurants_data)
    restaurants_data = engineer_restaurant_operation_dates(restaurants_data,is_prospects_data)
    restaurants_data = engineer_restaurant_active_on_jet_flag(restaurants_data)
    restaurants_data = engineer_restaurant_avg_menu_price(restaurants_data, menus_data)
    restaurants_data = engineer_restaurant_total_reviews(restaurants_data)
    restaurants_data = tidy_data(restaurants_data)
    return restaurants_data
