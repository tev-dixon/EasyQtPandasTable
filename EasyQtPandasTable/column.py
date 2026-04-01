from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional, TYPE_CHECKING

from PyQt6.QtCore import Qt

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QStyledItemDelegate
    from .filters import AbstractFilter


@dataclass
class ColumnDef:
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
    dtype: Optional[type] = None
    style: Optional[Callable[[Any], Optional[QColor]]] = None

    def __post_init__(self):
        if self.header is None:
            self.header = self.key
