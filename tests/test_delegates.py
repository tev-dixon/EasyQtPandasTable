"""Tests for CheckBoxDelegate and ButtonDelegate."""

from __future__ import annotations

from PyQt6.QtCore import Qt

from EasyQtPandasTable import ButtonDelegate, CheckBoxDelegate, ColumnDef, DataFrameTable
from conftest import _basic_columns


class TestCheckBoxDelegate:
    def test_toggle_via_model(self, qtbot, sample_df):
        delegate = CheckBoxDelegate()
        cols = _basic_columns()
        cols[3] = ColumnDef(key="active", header="Active", stretch=0.5, delegate=delegate)
        t = DataFrameTable(columns=cols)
        qtbot.addWidget(t)
        t.set_data(sample_df)

        m = t.table_model
        idx = m.index(0, 3)
        old_val = bool(idx.data(Qt.ItemDataRole.UserRole))
        m.setData(idx, not old_val, Qt.ItemDataRole.EditRole)
        assert bool(idx.data(Qt.ItemDataRole.UserRole)) == (not old_val)


class TestButtonDelegate:
    def test_callback_registration(self, qtbot, sample_df):
        clicked_rows = []
        delegate = ButtonDelegate(text="Go", on_click=lambda r: clicked_rows.append(r))
        cols = _basic_columns()
        cols.append(ColumnDef(key="btn", header="Action", delegate=delegate, stretch=1))
        t = DataFrameTable(columns=cols)
        qtbot.addWidget(t)
        t.set_data(sample_df)
        assert t.table_view.itemDelegateForColumn(5) is delegate
