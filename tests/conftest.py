import os
import sys

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

from src.models.density_models import RobustFeatureScaler
from src.models.walk_forward_pipeline import Q_COLS, X_COLS

DEV_PATH = os.path.join(REPO_ROOT, "output", "stage7_datasets", "spx_stage7_operational_development_2010_2019.csv")


@pytest.fixture(scope="session")
def dev_design():
    """In-sample development design matrices (2010-2019 supervised rows), scaled as in fit_insample_development."""
    df = pd.read_csv(DEV_PATH)
    rows = np.where(df["valid_supervised_pair_all5"].values)[0]
    y = df["target_y_next2"].iloc[rows].values
    Q = RobustFeatureScaler().fit_transform(df[Q_COLS].iloc[rows].values)
    X = RobustFeatureScaler().fit_transform(df[X_COLS].iloc[rows].values)
    return {
        "y": y,
        "rv": df["rv_20d"].iloc[rows].values,
        "Q": Q,
        "X": X,
        "QX": np.column_stack([Q, X]),
    }
