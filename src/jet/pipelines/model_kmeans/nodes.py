"""
This is a boilerplate pipeline 'model_kmeans'
generated using Kedro 0.18.12
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler


def create_kmeans_3(variables):
    km = KMeans(
        n_clusters=3, init="random", n_init=10, max_iter=300, tol=1e-04, random_state=0
    )
    km.fit(variables)
    return km


def create_kmeans_10(variables):
    km = KMeans(
        n_clusters=10, init="random", n_init=10, max_iter=300, tol=1e-04, random_state=0
    )
    km.fit(variables)
    return km


def predict_kmeans(km, new_data):
    predictions = pd.DataFrame(km.predict(new_data))
    return predictions


### visualise results
def get_feature_variance(n_data, o_data, clusters, km):
    n_data["clusters"] = clusters
    feature_means = n_data.groupby(["clusters"]).mean()
    feature_means = pd.DataFrame(
        StandardScaler().fit_transform(feature_means), columns=feature_means.columns
    )
    feature_means = feature_means.reset_index(names="clusters")
    feature_means = feature_means.melt(id_vars=["clusters"])
    feature_means["col_index"] = feature_means["variable"].apply(
        lambda x: n_data.columns.get_loc(x)
    )

    # Get the cluster labels
    cluster_labels = km.labels_

    # Calculate the mean of each cluster
    cluster_centroids = km.cluster_centers_

    # Identify the features that have the highest mean values in each cluster
    cluster_feature_importances = np.argsort(cluster_centroids, axis=1)[:, -3:]

    # Interpret the features with the highest mean values
    cluster_features = n_data.columns[cluster_feature_importances]

    # Get raw counts
    flattened_array = cluster_features.flatten()
    flattened_array = list(set(flattened_array))
    return feature_means, flattened_array, cluster_centroids, cluster_features


def get_clusters_top_features(cluster_centroids, cluster_features):
    # Print the cluster features
    output_str = "Features with highest mean values:"
    for cluster_index in range(len(cluster_centroids)):
        output_str += f" \n Cluster {cluster_index}: {cluster_features[cluster_index]}"
    return output_str


def feature_variance_outputs(n_data, o_data, clusters, flattened_array):
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
        "avg_main_price",
    ]
    o_data["clusters"] = clusters
    for feature in flattened_array:
        if feature in cols_numerical:
            t = o_data.groupby(["clusters"])[feature].mean().reset_index(name="mean")
            sns.barplot(data=t, x="clusters", y="mean", hue="clusters")
        else:
            t = (
                n_data.groupby(["clusters", feature])[feature]
                .size()
                .reset_index(name="count")
            )
            sns.barplot(data=t, x=feature, y="count", hue="clusters")
        plt.show()
    return


def feature_variance_plot(feature_means, flattened_array):
    # variance plot chart
    plt.figure(figsize=(5, 5))
    sns.barplot(
        data=feature_means[feature_means["variable"].isin(flattened_array)],
        y="variable",
        x="value",
        hue="clusters",
    )
    plt.xlabel("variance")
    return


def feature_variance(n_data, o_data, clusters, km):
    (
        feature_means,
        flattened_array,
        cluster_centroids,
        cluster_features,
    ) = get_feature_variance(n_data, o_data , clusters, km)
    feature_variance_plot(feature_means, flattened_array)
    return

def kmeans_plot(data_df,kmeans_name, data_x, rests_with_scores, clusters, km):
    i = int(kmeans_name.split('_')[1])
    #df = data_df.groupby([kmeans_name])["score"].mean().reset_index(name="mean")
    fig, axes = plt.subplots(1, 3, figsize=(20, 3))
    fig.suptitle(f"clusters={i}")
    sns.boxplot(data=data_df, x=kmeans_name, y="score", ax=axes[0])
    axes[0].set_ylim(0, 4)
    sns.countplot(data=data_df, x=kmeans_name, ax=axes[1])
    clusters_size_mean = (data_df.groupby([kmeans_name]).size()).mean()
    axes[1].axhline(y=clusters_size_mean, color="grey", linestyle="--")
    feature_means, flattened_array, cluster_centroids, cluster_features = get_feature_variance(data_x, rests_with_scores, clusters, km)
    sns.barplot(data=feature_means[feature_means['variable'].isin(flattened_array)], y='variable', x='value', hue='clusters', ax=axes[2])
    axes[2].legend_.remove()
    axes[2].set_ylabel(None)
    axes[2].set_xlabel('Standard deviation of cluster means')
    axes[2].set_position([0.85, 0.1, 0.3, 1])
    return fig

def get_top_features(data_x, rests_with_scores, clusters, km):
    (
            feature_means,
            flattened_array,
            cluster_centroids,
            cluster_features,
        ) = get_feature_variance(data_x, rests_with_scores, clusters, km)
    output = get_clusters_top_features(cluster_centroids, cluster_features)
    return output