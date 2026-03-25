"""Column definition for DataFrameTable."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional, TYPE_CHECKING

from PyQt6.QtCore import Qt

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QStyledItemDelegate
    from .filters import AbstractFilter


@dataclass
class ColumnDef:
    """Defines a single column in the table.

    Args:
        key: DataFrame column name.
        header: Display header text. Defaults to *key*.
        stretch: Relative width weight (e.g. 2 = twice as wide as 1).
        sortable: Allow sorting by clicking the header.
        filter_widget: An ``AbstractFilter`` instance for the filter bar.
        delegate: A ``QStyledItemDelegate`` for custom cell rendering.
        hidden: Start hidden.
        alignment: Qt alignment flags for cell text.
        formatter: ``(raw_value) -> str`` for display text.
        editable: Whether cells in this column accept edits.
    """

    key: str
    header: Optional[str] = None
    stretch: float = 1.0
    sortable: bool = False
    filter_widget: Optional["AbstractFilter"] = None
    delegate: Optional["QStyledItemDelegate"] = None
    hidden: bool = False
    alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
    formatter: Optional[Callable[[Any], str]] = None
    editable: bool = False

    def __post_init__(self):
        if self.header is None:
            self.header = self.key
