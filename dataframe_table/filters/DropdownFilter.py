from __future__ import annotations

from .AbstractFilter import AbstractFilter

from typing import Optional, Sequence, Callable

import numpy as np
import pandas as pd
from PyQt6.QtWidgets import QComboBox, QHBoxLayout

class _LazyComboBox(QComboBox):
    """QComboBox that calls a function to populate options on every popup open."""
 
    def __init__(self, options_fn: Callable[[], Sequence[str]], all_label: str, parent=None):
        super().__init__(parent)
        self._options_fn = options_fn
        self._all_label = all_label
 
    def showPopup(self):
        current = self.currentText()
        self.blockSignals(True)
        self.clear()
        self.addItem(self._all_label)
        for v in self._options_fn():
            self.addItem(str(v))
        idx = self.findText(current)
        self.setCurrentIndex(idx if idx >= 0 else 0)
        self.blockSignals(False)
        super().showPopup()
 
 
class DropdownFilter(AbstractFilter):
    """Dropdown that filters to a single selected value (or *All*).
 
    Operates in one of three mutually exclusive modes:
 
    1. **Auto** (default) — no ``options`` or ``options_fn``.  Options are
       populated from the DataFrame column via ``update_data()``, which is
       called automatically by ``DataFrameTable.set_data()``.
    2. **Fixed** — pass ``options=["A", "B", ...]``.  The list is set once
       at init time and never changes.  ``update_data()`` is a no-op.
    3. **Dynamic** — pass ``options_fn=my_callable``.  The callable is
       invoked every time the dropdown is opened (via ``showPopup``), so
       the list is always fresh.  ``update_data()`` is a no-op.
 
    Passing both ``options`` and ``options_fn`` raises ``ValueError``.
 
    .. warning::
 
       In dynamic mode, ``options_fn`` is called on the **main/UI thread**
       every time the user opens the dropdown.  If the callable is slow
       (e.g. an unindexed database query), it will block the interface
       until it returns.  Keep the function fast, or cache results
       externally and invalidate on your own schedule.
    """
 
    _ALL_LABEL = "(All)"
 
    def __init__(
        self,
        options: Optional[Sequence[str]] = None,
        options_fn: Optional[Callable[[], Sequence[str]]] = None,
        parent=None,
    ):
        if options is not None and options_fn is not None:
            raise ValueError("Pass 'options' or 'options_fn', not both.")
 
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
 
        if options_fn is not None:
            self._mode = "dynamic"
            self._combo = _LazyComboBox(options_fn, self._ALL_LABEL)
            self._combo.addItem(self._ALL_LABEL)
        else:
            self._mode = "fixed" if options is not None else "auto"
            self._combo = QComboBox()
            self._combo.addItem(self._ALL_LABEL)
            if options is not None:
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
        """Repopulate from data.  Only effective in auto mode."""
        if self._mode != "auto":
            return
        current = self._combo.currentText()
        self._combo.blockSignals(True)
        self._combo.clear()
        self._combo.addItem(self._ALL_LABEL)
        for v in sorted(series.dropna().unique(), key=str):
            self._combo.addItem(str(v))
        idx = self._combo.findText(current)
        self._combo.setCurrentIndex(idx if idx >= 0 else 0)
        self._combo.blockSignals(False)
