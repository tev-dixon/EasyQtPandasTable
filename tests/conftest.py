import os

os.environ.setdefault("PYTEST_QT_API", "pyqt6")
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import numpy as np
import pandas as pd
import pytest
from PyQt6.QtWidgets import QApplication

from EasyQtPandasTable import ColumnDef, DataFrameTable


def _sample_df(n: int = 100) -> pd.DataFrame:
    rng = np.random.RandomState(42)
    return pd.DataFrame({
        "id": np.arange(n),
        "name": [f"item_{i}" for i in range(n)],
        "value": rng.randint(0, 1000, size=n),
        "active": rng.choice([True, False], size=n),
        "category": rng.choice(["A", "B", "C"], size=n),
    })


def _basic_columns() -> list[ColumnDef]:
    return [
        ColumnDef(key="id", header="ID", stretch=0.5, sortable=True),
        ColumnDef(key="name", header="Name", stretch=2, sortable=True),
        ColumnDef(key="value", header="Value", stretch=1, sortable=True),
        ColumnDef(key="active", header="Active", stretch=0.5),
        ColumnDef(key="category", header="Cat", stretch=1, sortable=True),
    ]


@pytest.fixture
def sample_df():
    return _sample_df()


@pytest.fixture
def table(qtbot, sample_df):
    t = DataFrameTable(columns=_basic_columns())
    qtbot.addWidget(t)
    t.set_data(sample_df)
    t.show()
    t.resize(800, 400)
    QApplication.processEvents()
    return t
