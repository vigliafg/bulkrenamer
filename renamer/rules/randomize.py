from renamer.rules.base import RenameRule
from PyQt6.QtWidgets import QVBoxLayout, QSpinBox, QLineEdit, QComboBox, QLabel


class RandomizeRule(RenameRule):
    name = "Randomize"
    icon = "🎲"
    rule_type = "Randomize"

    def default_config(self):
        return {"type": "Randomize", "enabled": True, "length": 8,
                "chars": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                "where": "suffix", "separator": "_"}

    def _build_ui(self, layout: QVBoxLayout):
        layout.addWidget(QLabel("Random sequence length:"))
        self._len = QSpinBox(); self._len.setRange(1, 256); self._len.setValue(8)
        layout.addWidget(self._len)

        layout.addWidget(QLabel("Character set:"))
        self._chars = QLineEdit()
        self._chars.setText("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        layout.addWidget(self._chars)

        layout.addWidget(QLabel("Where:"))
        self._where = QComboBox(); self._where.addItems(["suffix", "prefix", "replace"])
        layout.addWidget(self._where)

        layout.addWidget(QLabel("Separator:"))
        self._sep = QLineEdit(); self._sep.setText("_")
        layout.addWidget(self._sep)

    def get_config(self):
        return {"type": "Randomize", "enabled": self.enabled(), "length": self._len.value(),
                "chars": self._chars.text(), "where": self._where.currentText(),
                "separator": self._sep.text()}

    def _push_config(self, config):
        if hasattr(self, '_len'): self._len.setValue(config.get('length', 8))
        if hasattr(self, '_chars'): self._chars.setText(config.get('chars', ''))
        if hasattr(self, '_where'):
            idx = self._where.findText(config.get('where', 'suffix'))
            if idx >= 0: self._where.setCurrentIndex(idx)
        if hasattr(self, '_sep'): self._sep.setText(config.get('separator', '_'))
