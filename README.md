# dataframe_table

A PyQt6 table widget backed by a pandas DataFrame, built for performance at tens of thousands of rows.

## Features

- **DataFrame-backed model** — data stays in pandas; sort and filter operate on a numpy index array (no copies).
- **Column definitions** — configure header text, stretch ratio, sortability, alignment, formatters, delegates, and filters per column via a simple `ColumnDef` dataclass.
- **Stretch ratios** — columns resize proportionally on window resize. A column with `stretch=2` is always twice the width of `stretch=1`.
- **Sorting** — click a sortable column header to toggle ascending/descending. Uses vectorised `argsort`.
- **Filter bar** — a hideable row of filter widgets aligned pixel-for-pixel to the columns below. Ships with `TextFilter`, `NumericFilter`, and `DropdownFilter`. Implement `AbstractFilter` for your own.
- **Painted delegates** — `CheckBoxDelegate` and `ButtonDelegate` render interactive controls via `paint()`/`editorEvent()` with zero per-row widget cost.
- **Row selection** — single, multi, or extended. `set_selected_rows()` and `get_selected_rows()` work with source DataFrame iloc indices. A `selection_changed` signal emits the current set.
- **Column visibility** — show/hide columns at runtime; stretch ratios and filter bar adjust automatically.
- **Styling** — `TableStyle` dataclass for alternating rows, grid, row height, font sizes, selection colour, and row numbers.

## Quick start

```bash
pip install -r requirements.txt
```

```python
import pandas as pd
from dataframe_table import (
    ColumnDef, DataFrameTable, TableStyle,
    TextFilter, NumericFilter, DropdownFilter,
    CheckBoxDelegate, ButtonDelegate,
)

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "score": [92, 87, 95],
    "active": [True, False, True],
    "team": ["Red", "Blue", "Red"],
})

table = DataFrameTable(
    columns=[
        ColumnDef(key="name", header="Name", stretch=2, sortable=True,
                  filter_widget=TextFilter()),
        ColumnDef(key="score", header="Score", stretch=1, sortable=True,
                  filter_widget=NumericFilter()),
        ColumnDef(key="active", header="Active", stretch=0.5,
                  delegate=CheckBoxDelegate()),
        ColumnDef(key="team", header="Team", stretch=1,
                  filter_widget=DropdownFilter()),
        ColumnDef(key="_actions", header="", stretch=0.5,
                  delegate=ButtonDelegate(text="Delete",
                                          on_click=lambda row: print(f"delete row {row}"))),
    ],
    selection_mode="extended",   # "single" | "multi" | "extended"
    style=TableStyle(row_height=32, alternating_rows=True),
)

table.set_data(df)
table.set_filter_bar_visible(True)
table.selection_changed.connect(lambda sel: print("selected:", sel))
table.show()
```

## API reference

### DataFrameTable

| Method / property | Description |
|---|---|
| `set_data(df)` | Load or replace the DataFrame. |
| `get_data() -> DataFrame` | Return a reference to the underlying DataFrame. |
| `update_cell(source_row, col_key, value)` | Update one cell by iloc index and column key. |
| `set_selected_rows(set[int])` | Programmatically select rows (source iloc indices). |
| `get_selected_rows() -> set[int]` | Get currently selected source iloc indices. |
| `selection_changed` signal | Emitted with `set[int]` on every selection change. |
| `set_column_visible(key, bool)` | Show or hide a column by key. |
| `set_filter_bar_visible(bool)` | Toggle the filter bar. |
| `reset_filters()` | Clear all active filters. |
| `table_view` | Direct access to the `QTableView`. |
| `table_model` | Direct access to the `DataFrameTableModel`. |

### ColumnDef

| Field | Type | Default | Purpose |
|---|---|---|---|
| `key` | `str` | *required* | DataFrame column name. |
| `header` | `str` | `key` | Display header text. |
| `stretch` | `float` | `1.0` | Relative width weight. |
| `sortable` | `bool` | `False` | Enable header-click sorting. |
| `filter_widget` | `AbstractFilter` | `None` | Filter for the filter bar. |
| `delegate` | `QStyledItemDelegate` | `None` | Custom cell renderer. |
| `hidden` | `bool` | `False` | Start hidden. |
| `alignment` | `Qt.AlignmentFlag` | left | Cell text alignment. |
| `formatter` | `(value) -> str` | `None` | Display text transform. |
| `editable` | `bool` | `False` | Allow inline editing. |

### Custom filters

Subclass `AbstractFilter` and implement:

```python
class MyFilter(AbstractFilter):
    def is_active(self) -> bool: ...
    def apply_filter(self, series: pd.Series) -> np.ndarray: ...  # bool array
    def reset(self) -> None: ...           # optional
    def update_data(self, series) -> None:  # optional, called on set_data()
```

Connect your widget's change signals to `self.filter_changed.emit()`.

## Running tests

```bash
pip install pytest pytest-qt
QT_QPA_PLATFORM=offscreen pytest tests/ -v
```

## Project structure

```
dataframe_table/
    __init__.py       Public exports
    column.py         ColumnDef dataclass
    model.py          QAbstractTableModel + view index array
    delegates.py      CheckBoxDelegate, ButtonDelegate
    filters.py        AbstractFilter, TextFilter, NumericFilter, DropdownFilter
    filter_bar.py     Horizontal filter bar synced to header widths
    widget.py         DataFrameTable (main widget), TableStyle
tests/
    test_dataframe_table.py   35 tests covering all features
requirements.txt
```
