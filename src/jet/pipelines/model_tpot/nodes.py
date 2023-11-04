"""
This is a boilerplate pipeline 'model_tpot'
generated using Kedro 0.18.12
"""

from typing import Dict

import pandas as pd
from tpot import TPOTRegressor
from sklearn.model_selection import KFold


def tpot_run(data_x: pd.DataFrame, data_y: pd.Series, parameters: Dict):
    data_y = data_y.values.ravel()
    cv = KFold(n_splits=10)
    tpot = TPOTRegressor(
        generations=5, population_size=100, verbosity=2, cv=cv, scoring="r2"
    )
    tpot.fit(data_x, data_y)
    return tpot.export()
