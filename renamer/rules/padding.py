from renamer.rules.base import RenameRule
from PyQt6.QtWidgets import QVBoxLayout, QComboBox, QSpinBox, QLineEdit, QLabel


class PaddingRule(RenameRule):
    name = "Padding"
    icon = "📏"
    rule_type = "Padding"

    def default_config(self):
        return {"type": "Padding", "enabled": True, "mode": "add_zero",
                "length": 3, "pad_char": " ", "position": "left"}

    def _build_ui(self, layout: QVBoxLayout):
        layout.addWidget(QLabel("Modalita':"))
        self._mode = QComboBox()
        self._mode.addItems(["add_zero", "remove_zero", "text_padding"])
        self._mode.currentTextChanged.connect(self._upd)
        layout.addWidget(self._mode)

        layout.addWidget(QLabel("Lunghezza:"))
        self._len = QSpinBox(); self._len.setRange(0, 999); self._len.setValue(3)
        layout.addWidget(self._len)

        layout.addWidget(QLabel("Carattere di padding:"))
        self._char = QLineEdit(); self._char.setText(" ")
        layout.addWidget(self._char)

        layout.addWidget(QLabel("Posizione:"))
        self._pos = QComboBox(); self._pos.addItems(["left", "right"])
        layout.addWidget(self._pos)
        self._upd()

    def _upd(self, *a):
        is_text = self._mode.currentText() == "text_padding"
        self._char.setVisible(is_text)
        self._pos.setVisible(is_text)

    def get_config(self):
        return {"type": "Padding", "enabled": self.enabled(), "mode": self._mode.currentText(),
                "length": self._len.value(), "pad_char": self._char.text(),
                "position": self._pos.currentText()}

    def _push_config(self, config):
        if hasattr(self, '_mode'):
            idx = self._mode.findText(config.get('mode', 'add_zero'))
            if idx >= 0: self._mode.setCurrentIndex(idx)
        if hasattr(self, '_len'): self._len.setValue(config.get('length', 3))
        if hasattr(self, '_char'): self._char.setText(config.get('pad_char', ' '))
        if hasattr(self, '_pos'):
            idx = self._pos.findText(config.get('position', 'left'))
            if idx >= 0: self._pos.setCurrentIndex(idx)
        if hasattr(self, '_upd'): self._upd()
