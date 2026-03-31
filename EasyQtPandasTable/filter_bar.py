from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QFrame, QSizePolicy, QTableView, QWidget

from .column import ColumnDef


class FilterBar(QFrame):

    _HEIGHT = 32
    _WIDGET_HEIGHT = 28

    def __init__(self, columns: List[ColumnDef], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._columns = columns
        self._table_view: Optional[QTableView] = None

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedHeight(self._HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)

        # Create widgets as direct children (no layout to avoid filter bar imposing sizing on parent)
        self._widgets: List[QWidget] = []
        for col in columns:
            w = col.filter_widget if col.filter_widget else QWidget()
            w.setParent(self)
            w.setFixedHeight(self._WIDGET_HEIGHT)
            self._widgets.append(w)

    def minimumSizeHint(self) -> QSize:
        return QSize(0, self._HEIGHT)

    def sizeHint(self) -> QSize:
        return QSize(0, self._HEIGHT)

    def bind_table_view(self, view: QTableView) -> None:
        self._table_view = view
        self.sync_widths()

    def sync_widths(self) -> None:
        if self._table_view is None:
            return
        header = self._table_view.horizontalHeader()
        vh = self._table_view.verticalHeader()

        # x offset = vertical header width + frame
        x = (vh.width() if vh.isVisible() else 0) + self._table_view.frameWidth()
        y = (self._HEIGHT - self._WIDGET_HEIGHT) // 2

        for i, w in enumerate(self._widgets):
            if header.isSectionHidden(i):
                w.hide()
            else:
                width = header.sectionSize(i)
                w.setGeometry(x, y, width, self._WIDGET_HEIGHT)
                w.show()
                x += width

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.sync_widths()
