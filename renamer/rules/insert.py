from renamer.rules.base import RenameRule
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QComboBox, QSpinBox, QLabel, QCheckBox, QHBoxLayout
from renamer.theme import C


class InsertRule(RenameRule):
    name = "Insert"
    icon = "📝"
    rule_type = "Insert"

    def default_config(self):
        return {"type": "Insert", "enabled": True, "text": "", "where": "prefix",
                "position": 1, "after_text": "", "before_text": "", "skip_extension": False}

    def _build_ui(self, layout: QVBoxLayout):
        self._text_edit = QLineEdit()
        self._text_edit.setPlaceholderText("Text to insert...")
        layout.addWidget(QLabel("Text to insert:"))
        layout.addWidget(self._text_edit)

        self._where_combo = QComboBox()
        self._where_combo.addItems(["prefix", "suffix", "position", "after_text", "before_text", "replace"])
        self._where_combo.currentTextChanged.connect(self._on_where_change)
        layout.addWidget(QLabel("Where:"))
        layout.addWidget(self._where_combo)

        self._pos_spin = QSpinBox()
        self._pos_spin.setRange(1, 9999)
        self._pos_spin.setValue(1)
        layout.addWidget(QLabel("Position (1-based):"))
        layout.addWidget(self._pos_spin)

        self._after_edit = QLineEdit()
        self._after_edit.setPlaceholderText("Text to insert after...")
        self._after_edit.setVisible(False)
        layout.addWidget(self._after_edit)

        self._before_edit = QLineEdit()
        self._before_edit.setPlaceholderText("Text to insert before...")
        self._before_edit.setVisible(False)
        layout.addWidget(self._before_edit)

        self._skip_ext = QCheckBox("Skip extension")
        layout.addWidget(self._skip_ext)
        self._on_where_change("prefix")

    def _on_where_change(self, val):
        self._pos_spin.setVisible(val == "position")
        self._after_edit.setVisible(val == "after_text")
        self._before_edit.setVisible(val == "before_text")

    def get_config(self):
        return {"type": "Insert", "enabled": self.enabled(), "text": self._text_edit.text(),
                "where": self._where_combo.currentText(), "position": self._pos_spin.value(),
                "after_text": self._after_edit.text(), "before_text": self._before_edit.text(),
                "skip_extension": self._skip_ext.isChecked()}

    def _push_config(self, config):
        """Push loaded config into UI widgets."""
        if hasattr(self, '_text_edit'):
            self._text_edit.setText(config.get('text', ''))
        if hasattr(self, '_where_combo'):
            where = config.get('where', 'prefix')
            idx = self._where_combo.findText(where)
            if idx >= 0:
                self._where_combo.setCurrentIndex(idx)
        if hasattr(self, '_pos_spin'):
            self._pos_spin.setValue(config.get('position', 1))
        if hasattr(self, '_after_edit'):
            self._after_edit.setText(config.get('after_text', ''))
        if hasattr(self, '_before_edit'):
            self._before_edit.setText(config.get('before_text', ''))
        if hasattr(self, '_skip_ext'):
            self._skip_ext.setChecked(config.get('skip_extension', False))
        if hasattr(self, '_on_where_change'):
            self._on_where_change(config.get('where', 'prefix'))
