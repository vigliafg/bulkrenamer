from renamer.rules.base import RenameRule
from PyQt6.QtWidgets import QVBoxLayout, QLineEdit, QComboBox, QLabel, QCheckBox
from renamer.theme import C


class RemoveRule(RenameRule):
    name = "Remove"
    icon = "🗑"
    rule_type = "Remove"

    def default_config(self):
        return {"type": "Remove", "enabled": True, "text": "", "occurrences": "all",
                "case_sensitive": False, "whole_words": False}

    def _build_ui(self, layout: QVBoxLayout):
        layout.addWidget(QLabel("Testo da rimuovere (usa *|* per multipli):"))
        self._text = QLineEdit()
        self._text.setPlaceholderText("testo1*|*testo2")
        layout.addWidget(self._text)

        layout.addWidget(QLabel("Occorrenze:"))
        self._occ = QComboBox()
        self._occ.addItems(["all", "first", "last"])
        layout.addWidget(self._occ)

        self._cs = QCheckBox("Case sensitive")
        layout.addWidget(self._cs)
        self._ww = QCheckBox("Solo parole intere")
        layout.addWidget(self._ww)

    def get_config(self):
        return {"type": "Remove", "enabled": self.enabled(), "text": self._text.text(),
                "occurrences": self._occ.currentText(), "case_sensitive": self._cs.isChecked(),
                "whole_words": self._ww.isChecked()}

    def _push_config(self, config):
        if hasattr(self, '_text'): self._text.setText(config.get('text', ''))
        if hasattr(self, '_occ'):
            idx = self._occ.findText(config.get('occurrences', 'all'))
            if idx >= 0: self._occ.setCurrentIndex(idx)
        if hasattr(self, '_cs'): self._cs.setChecked(config.get('case_sensitive', False))
        if hasattr(self, '_ww'): self._ww.setChecked(config.get('whole_words', False))
