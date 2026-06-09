from renamer.rules.base import RenameRule
from PyQt6.QtWidgets import QVBoxLayout, QComboBox, QLabel, QTextEdit
from renamer.engine import BUILTIN_TRANSLIT


class TranslitRule(RenameRule):
    name = "Translit"
    icon = "🌍"
    rule_type = "Translit"

    def default_config(self):
        return {"type": "Translit", "enabled": True, "alphabet": "",
                "custom_map": [], "direction": "forward"}

    def _build_ui(self, layout: QVBoxLayout):
        layout.addWidget(QLabel("Alfabeto / Lingua:"))
        self._alpha = QComboBox()
        self._alpha.addItem("(nessuno)")
        for name in BUILTIN_TRANSLIT:
            self._alpha.addItem(name)
        layout.addWidget(self._alpha)

        layout.addWidget(QLabel("Direzione:"))
        self._dir = QComboBox()
        self._dir.addItems(["forward", "backward"])
        layout.addWidget(self._dir)

        layout.addWidget(QLabel("Mappa custom (src=dst, una per riga):"))
        self._custom = QTextEdit()
        self._custom.setPlaceholderText("ä=ae\nö=oe\nü=ue\nß=ss")
        self._custom.setMaximumHeight(100)
        layout.addWidget(self._custom)

    def get_config(self):
        custom = []
        for line in self._custom.toPlainText().strip().split("\n"):
            line = line.strip()
            if "=" in line:
                parts = line.split("=", 1)
                if len(parts) == 2:
                    custom.append((parts[0], parts[1]))
        alphabet = self._alpha.currentText()
        if alphabet == "(nessuno)":
            alphabet = ""
        return {"type": "Translit", "enabled": self.enabled(),
                "alphabet": alphabet, "custom_map": custom,
                "direction": self._dir.currentText()}

    def _push_config(self, config):
        if hasattr(self, '_alpha'):
            alpha = config.get('alphabet', '')
            idx = self._alpha.findText(alpha if alpha else '(nessuno)')
            if idx >= 0: self._alpha.setCurrentIndex(idx)
        if hasattr(self, '_dir'):
            idx = self._dir.findText(config.get('direction', 'forward'))
            if idx >= 0: self._dir.setCurrentIndex(idx)
        if hasattr(self, '_custom'):
            custom_map = config.get('custom_map', [])
            text = "\n".join(f"{src}={dst}" for src, dst in custom_map)
            self._custom.setPlainText(text)
