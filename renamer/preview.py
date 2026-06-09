"""Preview table with live rename results."""

import os
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QWidget, QVBoxLayout,
    QLabel, QFrame, QSizePolicy, QCheckBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QBrush

from renamer.theme import C

# Highlight color for checked rows: a subtle blue-tinted surface
HL = "#3b3f5c"


class PreviewTable(QWidget):
    """Table showing original name, new name, status with live coloring."""

    row_selected = pyqtSignal(str, str)  # emits (old_full_path, new_full_path)
    checked_changed = pyqtSignal(int)    # emits checked count

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._paths: list[str] = []
        self._detail_visible = False
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Header
        hdr = QWidget()
        hdr_layout = QVBoxLayout(hdr)
        hdr_layout.setContentsMargins(0, 0, 0, 4)
        title = QLabel("FILES  /  RENAME PREVIEW")
        title.setProperty("heading", True)
        self._conflict_label = QLabel("")
        self._conflict_label.setProperty("conflict", True)

        hdr_row = QVBoxLayout()
        hdr_row.addWidget(title)
        hdr_row.addWidget(self._conflict_label)
        hdr_layout.addLayout(hdr_row)
        layout.addWidget(hdr)

        # Table (4 columns: ☑ | Original name | New name | Status)
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["☑", "Original name", "New name", "Status"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(0, 36)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(3, 110)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(False)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.itemSelectionChanged.connect(self._on_selection)
        # All-checked flag
        self._all_checked = False
        # Click on column-0 header toggles select-all
        self._table.horizontalHeader().sectionClicked.connect(self._on_header_click)
        layout.addWidget(self._table)

        # Detail panel (hidden initially)
        self._detail_frame = QFrame()
        self._detail_frame.setStyleSheet(
            f"QFrame {{ background-color: {C['surface0']}; border: 1px solid {C['surface1']}; "
            f"border-radius: 6px; padding: 8px; }}"
        )
        self._detail_frame.setVisible(False)
        detail_layout = QVBoxLayout(self._detail_frame)
        detail_layout.setContentsMargins(12, 8, 12, 8)

        dl1 = QLabel("📂 Original path:")
        dl1.setStyleSheet(f"font-weight: bold; color: {C['blue']}; font-size: 11px;")
        self._detail_orig = QLabel("")
        self._detail_orig.setStyleSheet(f"color: {C['text']}; font-size: 10px;")
        self._detail_orig.setWordWrap(True)

        dl2 = QLabel("🔄 New path:")
        dl2.setStyleSheet(f"font-weight: bold; color: {C['green']}; font-size: 11px;")
        self._detail_new = QLabel("")
        self._detail_new.setStyleSheet(f"color: {C['text']}; font-size: 10px;")
        self._detail_new.setWordWrap(True)

        detail_layout.addWidget(dl1)
        detail_layout.addWidget(self._detail_orig)
        detail_layout.addWidget(dl2)
        detail_layout.addWidget(self._detail_new)
        layout.addWidget(self._detail_frame)

    def set_preview_data(
        self,
        paths: list[str],
        new_names: list[str],
        conflicts_set: set[str],
        originals: list[str] | None = None,
    ) -> None:
        """Populate the table with rename preview data."""
        self._paths = paths
        self._all_checked = False
        block = self._table.blockSignals(True)
        self._table.setRowCount(0)
        self._table.setRowCount(len(paths))

        changed = 0
        for i, (fp, nuovo) in enumerate(zip(paths, new_names)):
            orig = originals[i] if originals and i < len(originals) else os.path.basename(fp)
            is_conflict = nuovo in conflicts_set
            is_changed = orig != nuovo

            # Column 0 — checkbox
            cb_item = QTableWidgetItem()
            cb_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            cb_item.setCheckState(Qt.CheckState.Unchecked)
            cb_item.setData(Qt.ItemDataRole.UserRole, fp)
            self._table.setItem(i, 0, cb_item)

            # Column 1 — original name
            orig_item = QTableWidgetItem(orig)
            orig_item.setData(Qt.ItemDataRole.UserRole, fp)
            orig_item.setForeground(QColor(C["text"]))

            # Column 2 — new name
            nuovo_item = QTableWidgetItem(nuovo)
            nuovo_item.setForeground(QColor(C["yellow"]))

            # Column 3 — status
            if is_conflict:
                stato = "⚠ duplicate"
                stato_color = C["red"]
            elif is_changed:
                stato = "✓"
                stato_color = C["green"]
                changed += 1
            else:
                stato = "—"
                stato_color = C["overlay1"]

            stato_item = QTableWidgetItem(stato)
            stato_item.setForeground(QColor(stato_color))
            stato_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self._table.setItem(i, 1, orig_item)
            self._table.setItem(i, 2, nuovo_item)
            self._table.setItem(i, 3, stato_item)
            self._table.setRowHeight(i, 26)

        self._table.blockSignals(block)
        # Connect itemChanged after populating to avoid mass signals
        try:
            self._table.itemChanged.disconnect()
        except TypeError:
            pass
        self._table.itemChanged.connect(self._on_check_toggled)
        # Reset header symbol
        hdr_item = self._table.horizontalHeaderItem(0)
        if hdr_item:
            hdr_item.setText("☐")

        # Update conflict label
        if conflicts_set:
            self._conflict_label.setText(
                f"⚠ {len(conflicts_set) if isinstance(conflicts_set, set) else sum(1 for n in new_names if n in conflicts_set)} conflicts — rename blocked"
            )
        else:
            self._conflict_label.setText("")

        total = len(paths)
        self._conflict_label.setVisible(bool(conflicts_set))

    # ── Checkbox logic ───────────────────────────────────────────────────

    def _on_header_click(self, section: int) -> None:
        """Toggle all checkboxes when column-0 header is clicked."""
        if section != 0 or self._table.rowCount() == 0:
            return
        self._all_checked = not self._all_checked
        new_state = Qt.CheckState.Checked if self._all_checked else Qt.CheckState.Unchecked
        block = self._table.blockSignals(True)
        for row in range(self._table.rowCount()):
            cb_item = self._table.item(row, 0)
            if cb_item:
                cb_item.setCheckState(new_state)
        self._table.blockSignals(block)
        self._apply_row_highlights()
        # Update header symbol
        hdr_item = self._table.horizontalHeaderItem(0)
        if hdr_item:
            hdr_item.setText("☑" if self._all_checked else "☐")
        self.checked_changed.emit(len(self.checked_paths()))

    def _on_check_toggled(self, item: QTableWidgetItem) -> None:
        """Single-row checkbox toggled — update highlight."""
        if item.column() == 0:
            self._apply_row_highlights()
            # Update header check state
            rc = self._table.rowCount()
            all_checked = rc > 0
            for row in range(rc):
                cb = self._table.item(row, 0)
                if cb and cb.checkState() != Qt.CheckState.Checked:
                    all_checked = False
                    break
            self._all_checked = all_checked
            hdr_item = self._table.horizontalHeaderItem(0)
            if hdr_item:
                hdr_item.setText("☑" if self._all_checked else "☐")
            self.checked_changed.emit(len(self.checked_paths()))

    def _apply_row_highlights(self) -> None:
        """Apply/remove background highlight for checked rows."""
        hl_brush = QBrush(QColor(HL))
        no_brush = QBrush(QColor(C["surface0"]))  # explicit table-background
        for row in range(self._table.rowCount()):
            cb_item = self._table.item(row, 0)
            checked = cb_item and cb_item.checkState() == Qt.CheckState.Checked
            brush = hl_brush if checked else no_brush
            for col in range(4):
                it = self._table.item(row, col)
                if it:
                    it.setBackground(brush)

    def checked_paths(self) -> list[str]:
        """Return full paths of checked rows."""
        result = []
        for row in range(self._table.rowCount()):
            cb = self._table.item(row, 0)
            if cb and cb.checkState() == Qt.CheckState.Checked and row < len(self._paths):
                result.append(self._paths[row])
        return result

    # ── Selection / detail ───────────────────────────────────────────────

    def _on_selection(self) -> None:
        """Show detail panel when a single row is selected."""
        rows = set(idx.row() for idx in self._table.selectedIndexes())
        if len(rows) != 1:
            self._detail_frame.setVisible(False)
            self._detail_visible = False
            return

        row = next(iter(rows))
        orig_item = self._table.item(row, 1)
        nuovo_item = self._table.item(row, 2)
        if not orig_item:
            self._detail_frame.setVisible(False)
            return

        fp = orig_item.data(Qt.ItemDataRole.UserRole)
        nuovo_name = nuovo_item.text() if nuovo_item else ""
        new_fp = os.path.join(os.path.dirname(fp), nuovo_name) if fp and nuovo_name else fp

        self._detail_orig.setText(str(fp))
        self._detail_new.setText(str(new_fp))
        self._detail_frame.setVisible(True)
        self._detail_visible = True
        self.row_selected.emit(str(fp or ""), str(new_fp or ""))

    def selected_paths(self) -> list[str]:
        """Return full paths of selected rows."""
        rows = set(idx.row() for idx in self._table.selectedIndexes())
        return [self._paths[i] for i in sorted(rows) if i < len(self._paths)]

    def clear(self) -> None:
        self._table.setRowCount(0)
        self._paths = []
        self._detail_frame.setVisible(False)
        self._conflict_label.setText("")
