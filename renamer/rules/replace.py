from renamer.rules.base import RenameRule
from PyQt6.QtWidgets import QVBoxLayout, QLineEdit, QComboBox, QLabel, QCheckBox
from renamer.theme import C


class ReplaceRule(RenameRule):
    name = "Replace"
    icon = "🔄"
    rule_type = "Replace"

    def default_config(self):
        return {"type": "Replace", "enabled": True, "find": "", "replace": "", "occurrences": "all",
                "case_sensitive": False, "whole_words": False, "use_wildcards": False, "use_regex": False}

    def _build_ui(self, layout: QVBoxLayout):
        layout.addWidget(QLabel("Trova (usa *|* per multipli):"))
        self._find = QLineEdit()
        self._find.setPlaceholderText("trova1*|*trova2")
        layout.addWidget(self._find)

        layout.addWidget(QLabel("Sostituisci:"))
        self._replace = QLineEdit()
        layout.addWidget(self._replace)

        layout.addWidget(QLabel("Occorrenze:"))
        self._occ = QComboBox()
        self._occ.addItems(["all", "first", "last"])
        layout.addWidget(self._occ)

        self._cs = QCheckBox("Case sensitive")
        layout.addWidget(self._cs)
        self._ww = QCheckBox("Solo parole intere")
        layout.addWidget(self._ww)
        self._wc = QCheckBox("Interpreta wildcard (*, ?)")
        layout.addWidget(self._wc)
        self._re = QCheckBox("Usa Regular Expression")
        layout.addWidget(self._re)

    def get_config(self):
        return {"type": "Replace", "enabled": self.enabled(), "find": self._find.text(),
                "replace": self._replace.text(), "occurrences": self._occ.currentText(),
                "case_sensitive": self._cs.isChecked(), "whole_words": self._ww.isChecked(),
                "use_wildcards": self._wc.isChecked(), "use_regex": self._re.isChecked()}

    def _push_config(self, config):
        if hasattr(self, '_find'): self._find.setText(config.get('find', ''))
        if hasattr(self, '_replace'): self._replace.setText(config.get('replace', ''))
        if hasattr(self, '_occ'):
            idx = self._occ.findText(config.get('occurrences', 'all'))
            if idx >= 0: self._occ.setCurrentIndex(idx)
        if hasattr(self, '_cs'): self._cs.setChecked(config.get('case_sensitive', False))
        if hasattr(self, '_ww'): self._ww.setChecked(config.get('whole_words', False))
        if hasattr(self, '_wc'): self._wc.setChecked(config.get('use_wildcards', False))
        if hasattr(self, '_re'): self._re.setChecked(config.get('use_regex', False))
