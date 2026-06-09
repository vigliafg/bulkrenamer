from renamer.rules.base import RenameRule
from PyQt6.QtWidgets import QVBoxLayout, QComboBox, QSpinBox, QLineEdit, QLabel, QCheckBox
from renamer.theme import C


class DeleteRule(RenameRule):
    name = "Delete"
    icon = "✂"
    rule_type = "Delete"

    def default_config(self):
        return {"type": "Delete", "enabled": True, "from_mode": "position", "from_val": 1,
                "from_delim": "", "until_mode": "count", "until_val": 0, "until_delim": "",
                "delete_current_name": False, "rtl": False, "keep_delimiters": False}

    def _build_ui(self, layout: QVBoxLayout):
        layout.addWidget(QLabel("From:"))
        self._from_mode = QComboBox()
        self._from_mode.addItems(["position", "delimiter"])
        self._from_mode.currentTextChanged.connect(self._upd)
        layout.addWidget(self._from_mode)
        self._from_val = QSpinBox()
        self._from_val.setRange(1, 9999)
        self._from_val.setValue(1)
        layout.addWidget(self._from_val)
        self._from_delim = QLineEdit()
        self._from_delim.setPlaceholderText("Delimiter...")
        layout.addWidget(self._from_delim)

        layout.addWidget(QLabel("Until:"))
        self._until_mode = QComboBox()
        self._until_mode.addItems(["count", "delimiter", "end"])
        self._until_mode.currentTextChanged.connect(self._upd)
        layout.addWidget(self._until_mode)
        self._until_val = QSpinBox()
        self._until_val.setRange(0, 9999)
        layout.addWidget(self._until_val)
        self._until_delim = QLineEdit()
        self._until_delim.setPlaceholderText("Delimiter...")
        layout.addWidget(self._until_delim)

        self._delete_all = QCheckBox("Delete current name")
        layout.addWidget(self._delete_all)
        self._rtl = QCheckBox("Right to left")
        layout.addWidget(self._rtl)
        self._keep = QCheckBox("Keep delimiters")
        layout.addWidget(self._keep)
        self._upd()

    def _upd(self, *a):
        fm = self._from_mode.currentText()
        self._from_val.setVisible(fm == "position")
        self._from_delim.setVisible(fm == "delimiter")
        um = self._until_mode.currentText()
        self._until_val.setVisible(um == "count")
        self._until_delim.setVisible(um == "delimiter")

    def get_config(self):
        return {"type": "Delete", "enabled": self.enabled(), "from_mode": self._from_mode.currentText(),
                "from_val": self._from_val.value(), "from_delim": self._from_delim.text(),
                "until_mode": self._until_mode.currentText(), "until_val": self._until_val.value(),
                "until_delim": self._until_delim.text(), "delete_current_name": self._delete_all.isChecked(),
                "rtl": self._rtl.isChecked(), "keep_delimiters": self._keep.isChecked()}

    def _push_config(self, config):
        if hasattr(self, '_from_mode'):
            idx = self._from_mode.findText(config.get('from_mode', 'position'))
            if idx >= 0: self._from_mode.setCurrentIndex(idx)
        if hasattr(self, '_from_val'): self._from_val.setValue(config.get('from_val', 1))
        if hasattr(self, '_from_delim'): self._from_delim.setText(config.get('from_delim', ''))
        if hasattr(self, '_until_mode'):
            idx = self._until_mode.findText(config.get('until_mode', 'count'))
            if idx >= 0: self._until_mode.setCurrentIndex(idx)
        if hasattr(self, '_until_val'): self._until_val.setValue(config.get('until_val', 0))
        if hasattr(self, '_until_delim'): self._until_delim.setText(config.get('until_delim', ''))
        if hasattr(self, '_delete_all'): self._delete_all.setChecked(config.get('delete_current_name', False))
        if hasattr(self, '_rtl'): self._rtl.setChecked(config.get('rtl', False))
        if hasattr(self, '_keep'): self._keep.setChecked(config.get('keep_delimiters', False))
        if hasattr(self, '_upd'): self._upd()
