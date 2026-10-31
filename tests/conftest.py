import os
import sys

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

from src.models.walk_forward_pipeline import build_refit_inputs

DEV_PATH = os.path.join(REPO_ROOT, "output", "stage7_datasets", "spx_stage7_operational_development_2010_2019.csv")


@pytest.fixture(scope="session")
def dev_design():
    """
    In-sample development design matrices: refit origin at the last 2019 row on development
    data only (2,231 supervised rows, the same rows as fit_insample_development).
    """
    df = pd.read_csv(DEV_PATH)
    refit = build_refit_inputs(df, len(df) - 1, len(df))
    return {
        "y": refit["y_train"],
        "rv": refit["rv_train"],
        "Q": refit["Q_train_scaled"],
        "X": refit["X_train_scaled"],
        "QX": refit["QX_train_scaled"],
        "QXpi": refit["QXpi_train"],
    }
