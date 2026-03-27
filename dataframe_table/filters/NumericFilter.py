from __future__ import annotations

from .AbstractFilter import AbstractFilter

import numpy as np
import pandas as pd
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLineEdit

class NumericFilter(AbstractFilter):
    """Numeric comparison filter (=, <, >, <=, >=, !=)."""

    OPS = ["=", "<", ">", "<=", ">=", "!="]

    def __init__(self, placeholder: str = "Value"):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(2)

        self._op = QComboBox()
        self._op.addItems(self.OPS)
        self._op.setFixedWidth(52)
        self._op.currentIndexChanged.connect(self._emit)
        layout.addWidget(self._op)

        self._edit = QLineEdit()
        self._edit.setPlaceholderText(placeholder)
        self._edit.textChanged.connect(self._emit)
        layout.addWidget(self._edit)

    def _emit(self):
        self.filter_changed.emit()

    def is_active(self) -> bool:
        try:
            float(self._edit.text())
            return True
        except (ValueError, TypeError):
            return False

    def reset(self) -> None:
        self._edit.clear()

    def apply_filter(self, series: pd.Series) -> np.ndarray:
        try:
            val = float(self._edit.text())
        except (ValueError, TypeError):
            return np.ones(len(series), dtype=bool)
        numeric = pd.to_numeric(series, errors="coerce")
        ops = {"=": numeric == val, "<": numeric < val, ">": numeric > val,
               "<=": numeric <= val, ">=": numeric >= val, "!=": numeric != val}
        result = ops.get(self._op.currentText(), pd.Series(np.ones(len(series), dtype=bool)))
        return result.fillna(False).values
