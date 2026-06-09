from renamer.rules.base import RenameRule
from PyQt6.QtWidgets import QVBoxLayout, QLineEdit, QComboBox, QLabel, QCheckBox


class StripRule(RenameRule):
    name = "Strip"
    icon = "✂"
    rule_type = "Strip"

    def default_config(self):
        return {"type": "Strip", "enabled": True, "chars": "", "sets": [],
                "positioning": "everywhere", "invert": False, "case_sensitive": False}

    def _build_ui(self, layout: QVBoxLayout):
        layout.addWidget(QLabel("Caratteri personalizzati:"))
        self._chars = QLineEdit()
        self._chars.setPlaceholderText("Caratteri da rimuovere...")
        layout.addWidget(self._chars)

        layout.addWidget(QLabel("Set predefiniti (seleziona uno o piu' nei menu):"))
        self._digits = QCheckBox("Cifre (0-9)")
        layout.addWidget(self._digits)
        self._symbols = QCheckBox("Simboli (!\"#$%...)")
        layout.addWidget(self._symbols)
        self._english = QCheckBox("Caratteri inglesi (a-z)")
        layout.addWidget(self._english)
        self._brackets = QCheckBox("Parentesi (){}[]<>")
        layout.addWidget(self._brackets)

        layout.addWidget(QLabel("Posizione:"))
        self._pos = QComboBox()
        self._pos.addItems(["everywhere", "leading", "trailing"])
        layout.addWidget(self._pos)

        self._inv = QCheckBox("Inverti (tieni solo i caratteri selezionati)")
        layout.addWidget(self._inv)
        self._cs = QCheckBox("Case sensitive")
        layout.addWidget(self._cs)

    def get_config(self):
        sets = []
        if self._digits.isChecked(): sets.append("digits")
        if self._symbols.isChecked(): sets.append("symbols")
        if self._english.isChecked(): sets.append("english")
        if self._brackets.isChecked(): sets.append("brackets")
        return {"type": "Strip", "enabled": self.enabled(), "chars": self._chars.text(),
                "sets": sets, "positioning": self._pos.currentText(),
                "invert": self._inv.isChecked(), "case_sensitive": self._cs.isChecked()}

    def _push_config(self, config):
        if hasattr(self, '_chars'): self._chars.setText(config.get('chars', ''))
        sets = config.get('sets', [])
        if hasattr(self, '_digits'): self._digits.setChecked('digits' in sets)
        if hasattr(self, '_symbols'): self._symbols.setChecked('symbols' in sets)
        if hasattr(self, '_english'): self._english.setChecked('english' in sets)
        if hasattr(self, '_brackets'): self._brackets.setChecked('brackets' in sets)
        if hasattr(self, '_pos'):
            idx = self._pos.findText(config.get('positioning', 'everywhere'))
            if idx >= 0: self._pos.setCurrentIndex(idx)
        if hasattr(self, '_inv'): self._inv.setChecked(config.get('invert', False))
        if hasattr(self, '_cs'): self._cs.setChecked(config.get('case_sensitive', False))
