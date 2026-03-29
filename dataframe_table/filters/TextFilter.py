from __future__ import annotations

from .AbstractFilter import AbstractFilter

import numpy as np
import pandas as pd
from PyQt6.QtWidgets import QHBoxLayout, QLineEdit

class TextFilter(AbstractFilter):

    def __init__(self, placeholder: str = "Filter…"):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(2)

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
        return s.str.contains(text, case=False, na=False).values
