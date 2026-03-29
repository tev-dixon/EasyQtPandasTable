from __future__ import annotations

from .AbstractFilter import AbstractFilter

import numpy as np
import pandas as pd
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLineEdit

class TextFilter(AbstractFilter):

    MODES = ["Contains", "Equals", "Regex"]

    def __init__(self, placeholder: str = "Filter…"):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(2)

        self._mode = QComboBox()
        self._mode.addItems(self.MODES)
        self._mode.setFixedWidth(80)
        self._mode.currentIndexChanged.connect(self._emit)
        layout.addWidget(self._mode)

        self._edit = QLineEdit()
        self._edit.setPlaceholderText(placeholder)
        self._edit.textChanged.connect(self._emit)
        layout.addWidget(self._edit)

    def _emit(self):
        self.filter_changed.emit()

    def is_active(self) -> bool:
        return bool(self._edit.text())

    def reset(self) -> None:
        self._edit.clear()

    def apply_filter(self, series: pd.Series) -> np.ndarray:
        text = self._edit.text()
        if not text:
            return np.ones(len(series), dtype=bool)
        s = series.astype(str)
        mode = self._mode.currentText()
        if mode == "Contains":
            return s.str.contains(text, case=False, na=False).values
        if mode == "Equals":
            return (s.str.lower() == text.lower()).values
        try:
            return s.str.contains(text, case=False, na=False, regex=True).values
        except Exception:
            return np.ones(len(series), dtype=bool)
