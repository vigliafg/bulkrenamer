from renamer.rules.base import RenameRule
from PyQt6.QtWidgets import QVBoxLayout, QComboBox, QLineEdit, QLabel, QCheckBox


class RearrangeRule(RenameRule):
    name = "Rearrange"
    icon = "🔀"
    rule_type = "Rearrange"

    def default_config(self):
        return {"type": "Rearrange", "enabled": True, "split_using": "delimiters",
                "delimiters": " - ", "positions": "", "new_pattern": "$1", "rtl": False}

    def _build_ui(self, layout: QVBoxLayout):
        layout.addWidget(QLabel("Dividi usando:"))
        self._split = QComboBox()
        self._split.addItems(["delimiters", "positions", "exact pattern"])
        self._split.currentTextChanged.connect(self._on_split)
        layout.addWidget(self._split)

        layout.addWidget(QLabel("Delimitatori (| per multipli):"))
        self._delims = QLineEdit()
        self._delims.setText(" - ")
        layout.addWidget(self._delims)

        layout.addWidget(QLabel("Posizioni (| per multipli) — solo per 'positions':"))
        self._positions = QLineEdit()
        self._positions.setVisible(False)
        layout.addWidget(self._positions)

        layout.addWidget(QLabel("Nuovo pattern ($1, $2, ..., $0=nome intero):"))
        self._pattern = QLineEdit()
        self._pattern.setText("$1")
        layout.addWidget(self._pattern)

        self._rtl = QCheckBox("Da destra a sinistra")
        layout.addWidget(self._rtl)
        self._on_split("delimiters")

    def _on_split(self, val):
        is_pos = val == "positions"
        self._delims.setVisible(not is_pos)
        self._positions.setVisible(is_pos)

    def get_config(self):
        return {"type": "Rearrange", "enabled": self.enabled(), "split_using": self._split.currentText(),
                "delimiters": self._delims.text(), "positions": self._positions.text(),
                "new_pattern": self._pattern.text(), "rtl": self._rtl.isChecked()}

    def _push_config(self, config):
        if hasattr(self, '_split'):
            idx = self._split.findText(config.get('split_using', 'delimiters'))
            if idx >= 0: self._split.setCurrentIndex(idx)
        if hasattr(self, '_delims'): self._delims.setText(config.get('delimiters', ' - '))
        if hasattr(self, '_positions'): self._positions.setText(config.get('positions', ''))
        if hasattr(self, '_pattern'): self._pattern.setText(config.get('new_pattern', '$1'))
        if hasattr(self, '_rtl'): self._rtl.setChecked(config.get('rtl', False))
        if hasattr(self, '_on_split'): self._on_split(config.get('split_using', 'delimiters'))
