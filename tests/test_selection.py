"""Tests for row selection — set, get, signal, and focus behaviour."""

from __future__ import annotations

from PyQt6.QtWidgets import QApplication


class TestSelection:
    def test_set_and_get_selection(self, table):
        table.set_selected_rows({0, 5, 10})
        assert table.get_selected_rows() == {0, 5, 10}

    def test_selection_changed_signal(self, qtbot, table):
        received = []
        table.selection_changed.connect(lambda s: received.append(s))
        table.set_selected_rows({3})
        QApplication.processEvents()
        assert len(received) > 0
        assert 3 in received[-1]

    def test_empty_selection(self, table):
        table.set_selected_rows(set())
        assert table.get_selected_rows() == set()

    def test_selection_after_sort(self, table):
        table.set_selected_rows({0, 1, 2})
        table.table_model.set_sort(2, ascending=True)
        table.table_model.rebuild_view()
        table.set_selected_rows({0, 1, 2})
        assert table.get_selected_rows() == {0, 1, 2}


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
        assert table.get_selected_rows() == {5, 6}, "old selection should be fully cleared"

    def test_empty_selection_after_nonempty(self, table):
        table.set_selected_rows({0, 1})
        QApplication.processEvents()
        table.set_selected_rows(set())
        QApplication.processEvents()
        assert table.get_selected_rows() == set()
