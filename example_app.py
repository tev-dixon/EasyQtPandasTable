"""Example app demonstrating DataFrameTable usage.

Run:  python example_app.py
"""

import sys
import numpy as np
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QLabel,
)

# ── Import everything you need from the package ──
from dataframe_table import (
    ColumnDef,
    DataFrameTable,
    TableStyle,
    TextFilter,
    NumericFilter,
    DropdownFilter,
    CheckBoxDelegate,
    ButtonDelegate,
)


def make_sample_data(n: int = 500) -> pd.DataFrame:
    rng = np.random.RandomState(0)
    return pd.DataFrame({
        "id": np.arange(n),
        "name": [f"Item {i}" for i in range(n)],
        "price": np.round(rng.uniform(5, 500, n), 2),
        "in_stock": rng.choice([True, False], n),
        "category": rng.choice(["Electronics", "Books", "Clothing", "Food"], n),
        # This column exists in the DF but won't be shown — demonstrating superset support
        "internal_sku": [f"SKU-{i:05d}" for i in range(n)],
    })


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataFrameTable Example")
        self.resize(1000, 600)

        # ── Define columns ──
        # Each ColumnDef maps to a DataFrame column by `key`.
        # Columns can have filters, delegates, formatters, etc.
        columns = [
            ColumnDef(
                key="id",
                header="ID",
                stretch=0.5,
                sortable=True,
            ),
            ColumnDef(
                key="name",
                header="Product Name",
                stretch=2.5,
                sortable=True,
                filter_widget=TextFilter(placeholder="Search names…"),
            ),
            ColumnDef(
                key="price",
                header="Price",
                stretch=1,
                sortable=True,
                filter_widget=NumericFilter(placeholder="e.g. 100"),
                formatter=lambda v: f"${v:,.2f}",
            ),
            ColumnDef(
                key="in_stock",
                header="In Stock",
                stretch=0.6,
                delegate=CheckBoxDelegate(),
            ),
            ColumnDef(
                key="category",
                header="Category",
                stretch=1.2,
                sortable=True,
                filter_widget=DropdownFilter(),  # auto-populates from data
            ),
            # Button column — key doesn't need to exist in the DF
            ColumnDef(
                key="_delete",
                header="",
                stretch=0.6,
                delegate=ButtonDelegate(
                    text="Delete",
                    on_click=self._on_delete_clicked,
                ),
            ),
        ]

        # ── Create the table ──
        self.table = DataFrameTable(
            columns=columns,
            selection_mode="extended",
            style=TableStyle(
                alternating_rows=True,
                row_height=30,
                grid_visible=True,
            ),
        )

        # ── Load data ──
        self.df = make_sample_data()
        self.table.set_data(self.df)

        # ── Connect selection signal ──
        self.table.selection_changed.connect(self._on_selection_changed)

        # ── Toolbar buttons ──
        btn_toggle_filters = QPushButton("Toggle Filters")
        btn_toggle_filters.clicked.connect(
            lambda: self.table.set_filter_bar_visible(not self.table.is_filter_bar_visible())
        )

        btn_reset_filters = QPushButton("Reset Filters")
        btn_reset_filters.clicked.connect(self.table.reset_filters)

        btn_hide_price = QPushButton("Toggle Price Column")
        btn_hide_price.clicked.connect(
            lambda: self.table.set_column_visible(
                "price", not self.table.is_column_visible("price")
            )
        )

        btn_select = QPushButton("Select rows 0, 2, 4")
        btn_select.clicked.connect(lambda: self.table.set_selected_rows({0, 2, 4}))

        btn_update = QPushButton("Set row 0 name → 'UPDATED'")
        btn_update.clicked.connect(lambda: self.table.update_cell(0, "name", "UPDATED"))

        self.status = QLabel("Selection: (none)")

        # ── Layout ──
        toolbar = QHBoxLayout()
        for btn in [btn_toggle_filters, btn_reset_filters, btn_hide_price, btn_select, btn_update]:
            toolbar.addWidget(btn)
        toolbar.addStretch()

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addLayout(toolbar)
        layout.addWidget(self.table)
        layout.addWidget(self.status)
        self.setCentralWidget(central)

    def _on_selection_changed(self, selected: set):
        if selected:
            self.status.setText(f"Selection: {sorted(selected)}")
        else:
            self.status.setText("Selection: (none)")

    def _on_delete_clicked(self, source_row: int):
        name = self.df.at[source_row, "name"]
        print(f"Delete clicked for row {source_row}: {name}")
        # In a real app you'd remove the row from the DF and call set_data() again


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
