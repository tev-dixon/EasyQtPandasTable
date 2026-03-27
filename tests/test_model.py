"""Tests for DataFrameTableModel — basics, sorting, bulk updates."""

from __future__ import annotations

from PyQt6.QtCore import Qt

from conftest import _sample_df


class TestModelBasics:
    def test_row_count(self, table, sample_df):
        assert table.table_model.rowCount() == len(sample_df)

    def test_column_count(self, table):
        assert table.table_model.columnCount() == 5

    def test_data_display(self, table):
        idx = table.table_model.index(0, 0)
        assert idx.data(Qt.ItemDataRole.DisplayRole) is not None

    def test_header_data(self, table):
        m = table.table_model
        assert m.headerData(0, Qt.Orientation.Horizontal) == "ID"
        assert m.headerData(1, Qt.Orientation.Horizontal) == "Name"

    def test_source_index_roundtrip(self, table):
        m = table.table_model
        for view_row in range(min(10, m.rowCount())):
            src = m.source_index(view_row)
            assert m.view_row_for_source(src) == view_row


class TestSorting:
    def test_sort_ascending(self, table):
        m = table.table_model
        m.set_sort(2, ascending=True)
        m.rebuild_view()
        values = [m.data(m.index(r, 2), Qt.ItemDataRole.UserRole) for r in range(m.rowCount())]
        assert values == sorted(values)

    def test_sort_descending(self, table):
        m = table.table_model
        m.set_sort(2, ascending=False)
        m.rebuild_view()
        values = [m.data(m.index(r, 2), Qt.ItemDataRole.UserRole) for r in range(m.rowCount())]
        assert values == sorted(values, reverse=True)

    def test_sort_preserves_row_count(self, table, sample_df):
        m = table.table_model
        m.set_sort(0, ascending=True)
        m.rebuild_view()
        assert m.rowCount() == len(sample_df)


class TestDataUpdate:
    def test_update_cell(self, table):
        table.update_cell(0, "name", "CHANGED")
        assert table.get_data().at[0, "name"] == "CHANGED"
        idx = table.table_model.index(0, 1)
        assert idx.data(Qt.ItemDataRole.DisplayRole) == "CHANGED"

    def test_update_nonexistent_column(self, table):
        table.update_cell(0, "nonexistent", "x")  # should not raise

    def test_set_new_data(self, qtbot, table):
        table.set_data(_sample_df(50))
        assert table.table_model.rowCount() == 50


class TestBulkUpdate:
    def test_bulk_update_changes_data(self, table):
        table.update_cells_bulk([
            (0, "name", "BULK_0"),
            (1, "name", "BULK_1"),
            (2, "value", 9999),
        ])
        df = table.get_data()
        assert df.at[0, "name"] == "BULK_0"
        assert df.at[1, "name"] == "BULK_1"
        assert df.at[2, "value"] == 9999

    def test_bulk_update_emits_once(self, table):
        signals = []
        table.table_model.layoutChanged.connect(lambda: signals.append(1))
        table.update_cells_bulk([
            (i, "name", f"ROW_{i}") for i in range(50)
        ])
        assert len(signals) == 1, f"layoutChanged emitted {len(signals)} times, expected 1"

    def test_bulk_update_skips_bad_columns(self, table):
        table.update_cells_bulk([
            (0, "nonexistent", "x"),
            (0, "name", "VALID"),
        ])
        assert table.get_data().at[0, "name"] == "VALID"
