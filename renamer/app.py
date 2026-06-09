"""Main Application Window — Bulk File Renamer PRO (PyQt6 clone of ReNamer)."""

import os
import json
import copy
from pathlib import Path
from typing import Any

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QStatusBar,
    QSplitter, QPushButton, QMenuBar, QMenu, QFileDialog, QMessageBox,
    QScrollArea, QFrame, QLabel, QSizePolicy, QCheckBox, QInputDialog,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QColor

from renamer.theme import C, QSS
from renamer.engine import apply_rules_stack
from renamer.undo import UndoManager
from renamer.preview import PreviewTable
from renamer.rules import ALL_RULES
from renamer.rules.base import RenameRule

FACTORY_C = copy.deepcopy(C)


class BulkRenamerProApp(QMainWindow):
    """Main window with rules panel, preview, toolbar, and menus."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Bulk File Renamer PRO")
        self.resize(1300, 750)
        self.setMinimumSize(960, 600)
        self.setStyleSheet(QSS)

        self._files: list[str] = []
        self._display_names: list[str] = []  # basenames to show in "Nome originale" column
        self._undo = UndoManager()
        self._rules: list[RenameRule] = []
        self._rule_widgets: list[QWidget] = []
        self._rule_wrappers: list[QFrame] = []

        self._build_menubar()
        self._build_toolbar()
        self._build_body()
        self._build_statusbar()

        # Add default rule
        self._add_rule()

    # ── Menu Bar ──────────────────────────────────────────────────────────

    def _build_menubar(self) -> None:
        mb = self.menuBar()

        file_menu = mb.addMenu("File")
        file_menu.addAction("📂 Apri cartella...", self._open_folder)
        file_menu.addAction("📄 Aggiungi file...", self._add_files)
        file_menu.addSeparator()
        file_menu.addAction("💾 Salva preset...", self._save_preset)
        file_menu.addAction("📂 Carica preset...", self._load_preset)
        file_menu.addSeparator()
        file_menu.addAction("Esci", self.close)

        rules_menu = mb.addMenu("Regole")
        for rule_cls in ALL_RULES:
            action = rules_menu.addAction(f"{rule_cls.icon} Aggiungi {rule_cls.name}",
                                          lambda rc=rule_cls: self._add_rule(rc))
        rules_menu.addSeparator()
        rules_menu.addAction("🗑 Rimuovi tutte le regole", self._clear_rules)

        tools_menu = mb.addMenu("Strumenti")
        tools_menu.addAction("▶ Anteprima", self._refresh_preview)
        tools_menu.addAction("✅ Rinomina!", self._rename)
        tools_menu.addAction("↩ Annulla", self._undo_last)
        tools_menu.addSeparator()
        tools_menu.addAction("↺ Factory Reset", self._factory_reset)

        help_menu = mb.addMenu("Aiuto")
        help_menu.addAction("ℹ Informazioni", self._show_about)

    # ── Toolbar ───────────────────────────────────────────────────────────

    def _build_toolbar(self) -> None:
        tb = QToolBar("Toolbar")
        tb.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tb)

        tb.addWidget(self._tbtn("📂 Cartella", self._open_folder, 120))
        tb.addWidget(self._tbtn("📄 File", self._add_files, 90))
        tb.addSeparator()
        tb.addWidget(self._tbtn_colored("▶ Anteprima", self._refresh_preview, 110, "info"))

    def _tbtn(self, text: str, callback, width: int = 100) -> QPushButton:
        b = QPushButton(text)
        b.setFixedWidth(width)
        b.clicked.connect(callback)
        return b

    def _tbtn_accent(self, text: str, callback, width: int = 140) -> QPushButton:
        b = QPushButton(text)
        b.setFixedWidth(width)
        b.setProperty("accent", True)
        b.setStyleSheet("")  # force re-style
        b.clicked.connect(callback)
        return b

    def _tbtn_colored(self, text: str, callback, width: int = 140, style: str = "danger") -> QPushButton:
        b = QPushButton(text)
        b.setFixedWidth(width)
        b.setProperty(style, True)
        b.setStyleSheet("")  # force re-style
        b.clicked.connect(callback)
        return b

    # ── Body (QSplitter: rules | preview) ────────────────────────────────

    def _build_body(self) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(4)
        self.setCentralWidget(splitter)

        # Left panel: rules stack (scrollable)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(6, 6, 3, 6)

        # Scrollable rules stack
        self._rules_scroll = QScrollArea()
        self._rules_scroll.setWidgetResizable(True)
        self._rules_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._rules_container = QWidget()
        self._rules_layout = QVBoxLayout(self._rules_container)
        self._rules_layout.setContentsMargins(0, 0, 0, 0)
        self._rules_layout.setSpacing(4)
        self._rules_layout.addStretch()
        self._rules_scroll.setWidget(self._rules_container)
        left_layout.addWidget(self._rules_scroll)

        splitter.addWidget(left)

        # Right panel: preview
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(3, 6, 6, 6)
        self._preview_table = PreviewTable()
        self._preview_table.checked_changed.connect(self._update_status_checked)
        right_layout.addWidget(self._preview_table)

        # Buttons under preview
        btn_row = QHBoxLayout()
        rem_btn = self._tbtn("🗑 Rimuovi selezionati", self._remove_checked, 180)
        rem_btn.setToolTip("Rimuove i file selezionati solo dalla lista — non cancella i file dal disco")
        btn_row.addWidget(rem_btn)
        btn_row.addWidget(self._tbtn("🔃 Ordina per nome", self._sort_by_name, 150))
        btn_row.addStretch()
        self._rename_btn = self._tbtn_colored("✅ Rinomina (0)", self._rename, 155, "danger")
        btn_row.addWidget(self._rename_btn)
        btn_row.addWidget(self._tbtn_colored("↩ Annulla", self._undo_last, 100, "success"))
        right_layout.addLayout(btn_row)

        splitter.addWidget(right)
        splitter.setSizes([self.width() // 3, self.width() * 2 // 3])
        splitter.setStretchFactor(0, 1)  # left panel gets 1/3
        splitter.setStretchFactor(1, 2)  # right panel gets 2/3

    # ── Status Bar ────────────────────────────────────────────────────────

    def _build_statusbar(self) -> None:
        self._status = QStatusBar()
        self._status.showMessage("Nessun file caricato. | Pronto.")
        self._last_changed = 0
        self._last_conflicts = 0
        self.setStatusBar(self._status)

    # ── Rule management ───────────────────────────────────────────────────

    def _add_rule(self, rule_cls: type[RenameRule] | None = None) -> None:
        if rule_cls is None:
            rule_cls = ALL_RULES[0]

        rule = rule_cls()
        wrapper = QFrame()
        wrapper.setFrameShape(QFrame.Shape.StyledPanel)
        wrapper.setStyleSheet(
            f"QFrame {{ background-color: {C['mantle']}; border: 1px solid {C['surface1']}; "
            f"border-radius: 8px; padding: 4px; margin: 2px 0; }}"
        )

        w_layout = QVBoxLayout(wrapper)
        w_layout.setContentsMargins(8, 4, 8, 6)

        # Header row
        hdr = QHBoxLayout()
        icon_label = QLabel(f"{rule_cls.icon}")
        icon_label.setStyleSheet(f"font-size: 16px;")
        name_label = QLabel(rule_cls.name)
        name_label.setStyleSheet(f"font-weight: bold; color: {C['blue']}; font-size: 13px;")
        enable_cb = QCheckBox("Abilitata")
        enable_cb.setChecked(True)
        enable_cb.toggled.connect(lambda v, r=rule: r.set_enabled(v))

        remove_btn = QPushButton("✕")
        remove_btn.setFixedSize(24, 24)
        remove_btn.setStyleSheet(
            f"QPushButton {{ background: {C['surface1']}; color: {C['red']}; "
            f"border: none; border-radius: 4px; font-weight: bold; }}"
            f"QPushButton:hover {{ background: {C['red']}; color: {C['base']}; }}"
        )
        remove_btn.clicked.connect(lambda _, w=wrapper: self._remove_rule(w))

        hdr.addWidget(icon_label)
        hdr.addWidget(name_label)
        hdr.addStretch()
        hdr.addWidget(enable_cb)
        hdr.addWidget(remove_btn)
        w_layout.addLayout(hdr)

        # Rule content widget
        content = rule.build_widget()
        w_layout.addWidget(content)

        self._rules_layout.insertWidget(self._rules_layout.count() - 1, wrapper)
        self._rules.append(rule)
        self._rule_widgets.append(content)
        self._rule_wrappers.append(wrapper)
        self._refresh_preview()

    def _remove_rule(self, wrapper: QFrame) -> None:
        idx = self._rule_wrappers.index(wrapper) if wrapper in self._rule_wrappers else -1
        if idx >= 0:
            self._rules_layout.removeWidget(wrapper)
            wrapper.deleteLater()
            del self._rules[idx]
            del self._rule_widgets[idx]
            del self._rule_wrappers[idx]
        self._refresh_preview()

    def _clear_rules(self) -> None:
        for w in list(self._rule_wrappers):
            self._rules_layout.removeWidget(w)
            w.deleteLater()
        self._rules.clear()
        self._rule_widgets.clear()
        self._rule_wrappers.clear()
        self._refresh_preview()

    def _collect_rules(self) -> list[dict[str, Any]]:
        return [r.get_config() for r in self._rules if r.enabled()]

    # ── File management ───────────────────────────────────────────────────

    def _open_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Seleziona cartella")
        if not folder:
            return
        self._files = sorted(
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f))
        )
        self._display_names = [os.path.basename(f) for f in self._files]
        self._refresh_preview()
        self._status.showMessage(f"{len(self._files)} file da: {folder}")

    def _add_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(self, "Aggiungi file")
        if not files:
            return
        existing = set(self._files)
        new_files = [f for f in files if f not in existing]
        self._files.extend(new_files)
        self._display_names.extend(os.path.basename(f) for f in new_files)
        self._refresh_preview()
        self._status.showMessage(f"{len(self._files)} file totali.")

    def _clear_files(self) -> None:
        self._files.clear()
        self._display_names.clear()
        self._preview_table.clear()
        self._status.showMessage("Lista svuotata.")

    def _remove_checked(self) -> None:
        """Remove checked files from the list."""
        paths = set(self._preview_table.checked_paths())
        if not paths:
            return
        indices = [i for i, p in enumerate(self._files) if p in paths]
        for i in sorted(indices, reverse=True):
            del self._files[i]
            del self._display_names[i]
        self._refresh_preview()

    def _sort_by_name(self) -> None:
        paired = sorted(zip(self._files, self._display_names), key=lambda x: x[1].lower())
        self._files = [p[0] for p in paired]
        self._display_names = [p[1] for p in paired]
        self._refresh_preview()

    def _update_status_checked(self, checked: int) -> None:
        """Update status bar and rename button when checkbox state changes (without full refresh)."""
        total = len(self._files)
        if total == 0:
            return
        self._rename_btn.setText(f"✅ Rinomina ({checked})")
        self._status.showMessage(
            f"☑ {checked}/{total} selezionati · "
            f"{self._last_changed} da rinominare · "
            f"{self._last_conflicts} conflitti"
        )

    # ── Preview ───────────────────────────────────────────────────────────

    def _refresh_preview(self) -> None:
        if not self._files:
            self._preview_table.clear()
            return

        rules = self._collect_rules()
        total = len(self._files)
        new_names: list[str] = []
        for i, fp in enumerate(self._files):
            try:
                nuovo = apply_rules_stack(fp, rules, i, total)
            except Exception as e:
                nuovo = f"[ERRORE: {e}]"
            new_names.append(nuovo)

        # Detect conflicts (duplicate new names)
        seen: dict[str, int] = {}
        for n in new_names:
            seen[n] = seen.get(n, 0) + 1
        conflicts = {n for n, cnt in seen.items() if cnt > 1}

        # Preserve checked state across refresh
        checked_set = set(self._preview_table.checked_paths())
        self._preview_table.set_preview_data(self._files, new_names, conflicts, self._display_names)
        # Restore checked state (block signals to avoid N redundant highlight passes)
        if checked_set:
            pt = self._preview_table
            block = pt._table.blockSignals(True)
            for row in range(pt._table.rowCount()):
                cb = pt._table.item(row, 0)
                if cb and cb.data(Qt.ItemDataRole.UserRole) in checked_set:
                    cb.setCheckState(Qt.CheckState.Checked)
            pt._table.blockSignals(block)
            pt._apply_row_highlights()
            # Recompute header + _all_checked flag
            rc = pt._table.rowCount()
            all_ok = rc > 0 and all(
                pt._table.item(r, 0) and pt._table.item(r, 0).checkState() == Qt.CheckState.Checked
                for r in range(rc)
            )
            pt._all_checked = all_ok
            hdr_item = pt._table.horizontalHeaderItem(0)
            if hdr_item:
                hdr_item.setText("☑" if all_ok else "☐")
        changed = sum(1 for fp, n in zip(self._files, new_names)
                      if os.path.basename(fp) != n)
        checked = len(checked_set)
        self._last_changed = changed
        self._last_conflicts = len(conflicts)
        self._rename_btn.setText(f"✅ Rinomina ({checked})")
        self._status.showMessage(
            f"☑ {checked}/{total} selezionati · {changed} da rinominare · {len(conflicts)} conflitti"
        )

    # ── Rename ────────────────────────────────────────────────────────────

    def _rename(self) -> None:
        if not self._files:
            QMessageBox.warning(self, "Bulk Renamer", "Nessun file nella lista.")
            return

        # Rinomina solo i file selezionati con la checkbox
        checked = self._preview_table.checked_paths()
        if not checked:
            QMessageBox.warning(self, "Bulk Renamer",
                "Nessun file selezionato.\nSpunta le checkbox nella preview per selezionare i file da rinominare.")
            return

        rules = self._collect_rules()
        total = len(checked)
        pairs = [
            (fp, apply_rules_stack(fp, rules, i, total))
            for i, fp in enumerate(checked)
        ]

        new_names = [n for _, n in pairs]
        if len(set(new_names)) < len(new_names):
            QMessageBox.critical(self, "Conflitti",
                "Nomi duplicati nel risultato.\nRisolvi i conflitti prima di procedere.")
            return

        to_change = [(fp, n) for fp, n in pairs if os.path.basename(fp) != n]
        if not to_change:
            QMessageBox.information(self, "Bulk Renamer", "Nessun file da rinominare.")
            return

        reply = QMessageBox.question(self, "Conferma",
            f"Rinominare {len(to_change)} file?\nOperazione reversibile con Annulla.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        done, errors = [], []
        for fp, new_name in to_change:
            new_fp = os.path.join(os.path.dirname(fp), new_name)
            try:
                os.rename(fp, new_fp)
                done.append((fp, new_fp))
                self._files[self._files.index(fp)] = new_fp
            except Exception as e:
                errors.append(f"{os.path.basename(fp)}: {e}")

        if done:
            self._undo.push(done)

        self._refresh_preview()
        msg = f"✅ Rinominati: {len(done)} file."
        if errors:
            msg += f"\n\n⚠ Errori ({len(errors)}):\n" + "\n".join(errors[:10])
        QMessageBox.information(self, "Completato", msg)

    def _undo_last(self) -> None:
        if not self._undo.can_undo():
            QMessageBox.information(self, "Annulla", "Nessuna operazione da annullare.")
            return
        restored, errors = self._undo.undo_last(self._files)
        self._refresh_preview()
        msg = f"↩ Ripristinati: {restored} file."
        if errors:
            msg += f"\n\n⚠ Errori:\n" + "\n".join(errors[:10])
        QMessageBox.information(self, "Annulla", msg)

    # ── Preset ────────────────────────────────────────────────────────────

    def _save_preset(self) -> None:
        name, ok = QInputDialog.getText(self, "Salva Preset", "Nome del preset:")
        if not ok or not name:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Salva preset", f"{name}.json", "JSON (*.json)")
        if not path:
            return
        preset = {"name": name, "rules": [r.get_config() for r in self._rules]}
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(preset, f, indent=2, ensure_ascii=False)
            QMessageBox.information(self, "Preset", f"Preset '{name}' salvato!")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile salvare: {e}")

    def _load_preset(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Carica preset", os.path.expanduser("~"), "JSON (*.json)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                preset = json.load(f)
            self._clear_rules()
            for cfg in preset.get("rules", []):
                rule_type = cfg.get("type", "")
                rule_cls = next((rc for rc in ALL_RULES if rc.rule_type == rule_type), None)
                if rule_cls:
                    rule = rule_cls()
                    rule.set_config(cfg)
                    # We need to add it via the UI... for now, use _add_rule differently
                    # Quick path: just add with config
                    self._add_rule_with_config(rule_cls, cfg)
            name = preset.get("name", os.path.basename(path))
            QMessageBox.information(self, "Preset", f"Preset '{name}' caricato!")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile caricare: {e}")

    def _add_rule_with_config(self, rule_cls: type[RenameRule], config: dict) -> None:
        """Add a rule and immediately set its config."""
        self._add_rule(rule_cls)
        if self._rules:
            self._rules[-1].set_config(config)

    # ── Factory reset ─────────────────────────────────────────────────────

    def _factory_reset(self) -> None:
        reply = QMessageBox.question(self, "Ripristino",
            "Ripristinare TUTTE le regole ai valori di default?\n"
            "Questa azione non puo' essere annullata.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._clear_rules()
        self._add_rule()
        QMessageBox.information(self, "Ripristino", "Regole ripristinate ai default.")

    def _show_about(self) -> None:
        QMessageBox.about(self, "Bulk File Renamer PRO",
            "Bulk File Renamer PRO v3.0 (PyQt6)\n\n"
            "Clone di ReNamer (den4b.com) con tutte le 17 regole.\n"
            "Tema: Catppuccin Mocha\n"
            "Basato su PyQt6.\n\n"
            "Funzionalita' principali:\n"
            "• 17 regole di rinominazione\n"
            "• Stack di regole componibili\n"
            "• Preview live con colori per colonna\n"
            "• Undo illimitato\n"
            "• Preset salvabili\n"
            "• Tema scuro Catppuccin Mocha\n\n"
            "Dipendenze: pip install PyQt6")
