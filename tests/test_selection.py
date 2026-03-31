"""Tests for row selection — set, get, signal, and focus behaviour."""

from __future__ import annotations

from PyQt6.QtWidgets import QApplication


class TestSelection:
    def test_set_and_get_selection(self, table):
        table.set_selected_rows({0, 5, 10})
        assert table.get_selected_row_indexes() == {0, 5, 10}

    def test_selection_changed_signal(self, qtbot, table):
        received = []
        table.selection_changed.connect(lambda s: received.append(s))
        table.set_selected_rows({3})
        QApplication.processEvents()
        assert len(received) > 0
        assert 3 in received[-1]

    def test_empty_selection(self, table):
        table.set_selected_rows(set())
        assert table.get_selected_row_indexes() == set()

    def test_selection_after_sort(self, table):
        table.set_selected_rows({0, 1, 2})
        table.table_model.set_sort(2, ascending=True)
        table.table_model.rebuild_view()
        table.set_selected_rows({0, 1, 2})
        assert table.get_selected_row_indexes() == {0, 1, 2}


class TestRegressionSelection:
    """Fix: programmatic selection must appear with the active (focused) palette."""

    def test_selection_gives_focus(self, table):
        table.set_selected_rows({0, 1})
        QApplication.processEvents()
        assert table.table_view.hasFocus()

    def test_selection_sets_current_index(self, table):
        table.set_selected_rows({3, 5})
        QApplication.processEvents()
        current = table.table_view.selectionModel().currentIndex()
        assert current.isValid(), "currentIndex should be set after programmatic selection"

    def test_selection_uses_clearandselect(self, table):
        table.set_selected_rows({0, 1, 2})
        QApplication.processEvents()
        table.set_selected_rows({5, 6})
        QApplication.processEvents()
        assert table.get_selected_row_indexes() == {5, 6}, "old selection should be fully cleared"

    def test_empty_selection_after_nonempty(self, table):
        table.set_selected_rows({0, 1})
        QApplication.processEvents()
        table.set_selected_rows(set())
        QApplication.processEvents()
        assert table.get_selected_row_indexes() == set()


class TestSelectFirstVisibleRow:
    def test_selects_first_row(self, table):
        src = table.select_first_visible_row()
        assert src is not None
        assert table.get_selected_row_indexes() == {src}

    def test_returns_source_index(self, table):
        src = table.select_first_visible_row()
        assert src == table.table_model.source_index(0)

    def test_returns_none_on_empty(self, qtbot):
        import pandas as pd
        from EasyQtPandasTable import DataFrameTable
        from conftest import _basic_columns
        t = DataFrameTable(columns=_basic_columns())
        qtbot.addWidget(t)
        t.set_data(pd.DataFrame())
        assert t.select_first_visible_row() is None
        assert t.get_selected_row_indexes() == set()

    def test_respects_sort(self, table):
        table.table_model.set_sort(2, ascending=True)
        table.table_model.rebuild_view()
        src = table.select_first_visible_row()
        # Should be the row with the smallest value, not source row 0
        assert src == table.table_model.source_index(0)
        assert table.get_selected_row_indexes() == {src}

    def test_respects_filter(self, qtbot, sample_df):
        from EasyQtPandasTable import ColumnDef, DataFrameTable, NumericFilter
        from conftest import _basic_columns
        nf = NumericFilter()
        cols = _basic_columns()
        cols[2] = ColumnDef(key="value", header="Value", stretch=1, filter_widget=nf)
        t = DataFrameTable(columns=cols)
        qtbot.addWidget(t)
        t.set_data(sample_df)

        nf._op.setCurrentText(">")
        nf._edit.setText("900")
        QApplication.processEvents()

        src = t.select_first_visible_row()
        assert src is not None
        # The selected row must actually pass the filter
        assert sample_df.at[src, "value"] > 900
