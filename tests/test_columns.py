"""Tests for column visibility, stretch ratios, and show/hide regressions."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication


class TestColumnVisibility:
    def test_hide_column(self, table):
        table.set_column_visible("name", False)
        assert not table.is_column_visible("name")
        assert table.table_view.isColumnHidden(1)

    def test_show_column(self, table):
        table.set_column_visible("name", False)
        table.set_column_visible("name", True)
        assert table.is_column_visible("name")

    def test_hide_preserves_data(self, table):
        table.set_column_visible("value", False)
        idx = table.table_model.index(0, 2)
        assert idx.data(Qt.ItemDataRole.UserRole) is not None


class TestStretchRatios:
    def test_stretch_proportional(self, table):
        QApplication.processEvents()
        header = table.table_view.horizontalHeader()
        w0 = header.sectionSize(0)  # stretch=0.5
        w1 = header.sectionSize(1)  # stretch=2
        assert w1 > w0

    def test_resize_redistributes(self, qtbot, table):
        table.resize(1200, 400)
        QApplication.processEvents()
        table._do_stretch()
        header = table.table_view.horizontalHeader()
        total = sum(header.sectionSize(i) for i in range(5))
        viewport_w = table.table_view.viewport().width()
        assert abs(total - viewport_w) < 10


class TestRegressionColumnShowHide:
    """Fix: show/hide column must redistribute within viewport, not expand it."""

    def test_show_hidden_column_stays_within_viewport(self, table):
        QApplication.processEvents()
        header = table.table_view.horizontalHeader()
        viewport_w = table.table_view.viewport().width()

        table.set_column_visible("name", False)
        QApplication.processEvents()
        table.set_column_visible("name", True)
        QApplication.processEvents()

        total = sum(header.sectionSize(i) for i in range(5) if not table.table_view.isColumnHidden(i))
        assert total <= viewport_w + 5, f"columns total {total} exceeds viewport {viewport_w}"

    def test_hide_show_cycle_preserves_ratios(self, table):
        QApplication.processEvents()
        header = table.table_view.horizontalHeader()

        table.set_column_visible("value", False)
        QApplication.processEvents()
        table.set_column_visible("value", True)
        QApplication.processEvents()

        # Ratios: ID=0.5, Name=2 → Name should be ~4x ID
        w_id = header.sectionSize(0)
        w_name = header.sectionSize(1)
        ratio = w_name / max(w_id, 1)
        assert 3.0 <= ratio <= 5.0, f"stretch ratio Name/ID = {ratio}, expected ~4"
