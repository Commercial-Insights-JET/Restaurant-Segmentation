"""
This is a boilerplate pipeline 'model_aspidx'
generated using Kedro 0.18.12
"""

import logging
from typing import Dict

import pandas as pd
from xgboost import XGBRegressor

from sklearn.model_selection import cross_val_predict
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error

import matplotlib.pyplot as plt
from sklearn.metrics import PredictionErrorDisplay


def train_model_xgb(data_x: pd.DataFrame, data_y: pd.Series):
    algo = XGBRegressor(
        learning_rate=0.5,
        max_depth=6,
        min_child_weight=14,
        n_estimators=100,
        n_jobs=1,
        objective="reg:squarederror",
        subsample=1.0,
        verbosity=0,
    )
    algo.fit(data_x, data_y.values.ravel())
    return algo


def evaluate_model(data_y: pd.Series, pred_y: pd.Series):
    data_y = data_y.values.ravel()
    scores = {}
    scores["R2"] = {"value": r2_score(data_y, pred_y), "step": 1}
    scores["MAE"] = {"value": mean_absolute_error(data_y, pred_y), "step": 1}
    scores["MSE"] = {"value": mean_squared_error(data_y, pred_y), "step": 1}
    logger = logging.getLogger(__name__)
    logger.info(
        f"Model has a coefficient R^2 of {scores['R2']['value'].round(3)} on test data.",
    )
    return scores


def prediction_output(algo, data_x: pd.DataFrame, data_y: pd.Series, parameters: Dict):
    pred_y = pd.Series(
        cross_val_predict(
            algo, data_x, data_y.values.ravel(), cv=parameters["cv_folds"]
        )
    ).rename("predicted_score")
    return pred_y


def visualise_predictions(data_y, pred_y, algo_name: None):
    data_y = data_y["score"].to_numpy()
    pred_y = pred_y["predicted_score"].to_numpy()
    fig, axs = plt.subplots(ncols=2, figsize=(6, 3))
    PredictionErrorDisplay.from_predictions(
        data_y,
        y_pred=pred_y,
        kind="actual_vs_predicted",
        subsample=100,
        ax=axs[0],
        random_state=0,
    )
    axs[0].set_title("Actual vs. Predicted values")
    PredictionErrorDisplay.from_predictions(
        data_y,
        y_pred=pred_y,
        kind="residual_vs_predicted",
        subsample=100,
        ax=axs[1],
        random_state=0,
    )
    axs[1].set_title("Residuals vs. Predicted Values")
    fig.suptitle(f"{algo_name} cross-validated predictions")
    plt.tight_layout()
    return fig



