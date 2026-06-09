from renamer.rules.base import RenameRule
from PyQt6.QtWidgets import QVBoxLayout, QComboBox, QLineEdit, QLabel, QCheckBox


class CaseRule(RenameRule):
    name = "Case"
    icon = "🔠"
    rule_type = "Case"

    def default_config(self):
        return {"type": "Case", "enabled": True, "case_mode": "none",
                "force_fragments": "", "skip_extension": False}

    def _build_ui(self, layout: QVBoxLayout):
        layout.addWidget(QLabel("Trasformazione:"))
        self._mode = QComboBox()
        self._mode.addItems(["none", "lowercase", "uppercase", "title",
                              "invert", "first_capital", "sentence"])
        layout.addWidget(self._mode)

        layout.addWidget(QLabel("Forza case per frammenti (separati da virgola):"))
        self._force = QLineEdit()
        self._force.setPlaceholderText("es: CD,DVD,SMS,PhD,iPad")
        layout.addWidget(self._force)

        self._skip = QCheckBox("Salta estensione")
        layout.addWidget(self._skip)

    def get_config(self):
        return {"type": "Case", "enabled": self.enabled(), "case_mode": self._mode.currentText(),
                "force_fragments": self._force.text(), "skip_extension": self._skip.isChecked()}

    def _push_config(self, config):
        if hasattr(self, '_mode'):
            idx = self._mode.findText(config.get('case_mode', 'none'))
            if idx >= 0: self._mode.setCurrentIndex(idx)
        if hasattr(self, '_force'): self._force.setText(config.get('force_fragments', ''))
        if hasattr(self, '_skip'): self._skip.setChecked(config.get('skip_extension', False))
