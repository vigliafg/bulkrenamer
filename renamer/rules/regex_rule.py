from renamer.rules.base import RenameRule
from PyQt6.QtWidgets import QVBoxLayout, QLineEdit, QSpinBox, QLabel


class RegexRule(RenameRule):
    name = "Regular Expressions"
    icon = "🔣"
    rule_type = "Regex"

    def default_config(self):
        return {"type": "Regex", "enabled": True, "pattern": "",
                "replacement": "", "count": 0}

    def _build_ui(self, layout: QVBoxLayout):
        layout.addWidget(QLabel("Regex pattern:"))
        self._pat = QLineEdit()
        self._pat.setPlaceholderText("e.g. (\\d{4})-(\\d{2})-(\\d{2})")
        layout.addWidget(self._pat)

        layout.addWidget(QLabel("Replacement:"))
        self._rep = QLineEdit()
        self._rep.setPlaceholderText("e.g. \\3-\\2-\\1")
        layout.addWidget(self._rep)

        layout.addWidget(QLabel("Count (0=unlimited):"))
        self._cnt = QSpinBox()
        self._cnt.setRange(0, 9999)
        layout.addWidget(self._cnt)

    def get_config(self):
        return {"type": "Regex", "enabled": self.enabled(),
                "pattern": self._pat.text(), "replacement": self._rep.text(),
                "count": self._cnt.value()}

    def _push_config(self, config):
        if hasattr(self, '_pat'): self._pat.setText(config.get('pattern', ''))
        if hasattr(self, '_rep'): self._rep.setText(config.get('replacement', ''))
        if hasattr(self, '_cnt'): self._cnt.setValue(config.get('count', 0))
