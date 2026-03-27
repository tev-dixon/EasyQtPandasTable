from __future__ import annotations

from .AbstractFilter import AbstractFilter

from typing import Optional, Sequence

import numpy as np
import pandas as pd
from PyQt6.QtWidgets import QComboBox, QHBoxLayout

class DropdownFilter(AbstractFilter):
    """Dropdown that filters to a single selected value (or *All*)."""

    _ALL_LABEL = "(All)"

    def __init__(self, options: Optional[Sequence[str]] = None):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)

        self._combo = QComboBox()
        self._combo.addItem(self._ALL_LABEL)
        if options:
            for o in options:
                self._combo.addItem(str(o))
        self._combo.currentIndexChanged.connect(lambda _: self.filter_changed.emit())
        layout.addWidget(self._combo)

    def is_active(self) -> bool:
        return self._combo.currentText() != self._ALL_LABEL

    def reset(self) -> None:
        self._combo.setCurrentIndex(0)

    def apply_filter(self, series: pd.Series) -> np.ndarray:
        selected = self._combo.currentText()
        if selected == self._ALL_LABEL:
            return np.ones(len(series), dtype=bool)
        return (series.astype(str) == selected).values

    def update_data(self, series: pd.Series) -> None:
        current = self._combo.currentText()
        self._combo.blockSignals(True)
        self._combo.clear()
        self._combo.addItem(self._ALL_LABEL)
        for v in sorted(series.dropna().unique(), key=str):
            self._combo.addItem(str(v))
        idx = self._combo.findText(current)
        self._combo.setCurrentIndex(idx if idx >= 0 else 0)
        self._combo.blockSignals(False)
