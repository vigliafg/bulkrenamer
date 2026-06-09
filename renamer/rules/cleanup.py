from renamer.rules.base import RenameRule
from PyQt6.QtWidgets import QVBoxLayout, QCheckBox, QLineEdit, QLabel


class CleanUpRule(RenameRule):
    name = "Clean Up"
    icon = "🧹"
    rule_type = "CleanUp"

    def default_config(self):
        return {"type": "CleanUp", "enabled": True, "strip_brackets": [],
                "replace_with_space": "", "fix_spaces": True, "normalize_unicode": False,
                "strip_emoji": False, "strip_marks": False, "camel_case_split": False}

    def _build_ui(self, layout: QVBoxLayout):
        layout.addWidget(QLabel("Remove bracket content:"))
        self._cb1 = QCheckBox("Round (...)"); layout.addWidget(self._cb1)
        self._cb2 = QCheckBox("Square [...]"); layout.addWidget(self._cb2)
        self._cb3 = QCheckBox("Curly {...}"); layout.addWidget(self._cb3)

        layout.addWidget(QLabel("Replace with spaces (characters):"))
        self._rws = QLineEdit(); self._rws.setPlaceholderText("e.g. ._-")
        layout.addWidget(self._rws)

        self._fs = QCheckBox("Fix multiple spaces")
        self._fs.setChecked(True); layout.addWidget(self._fs)
        self._nu = QCheckBox("Normalize unicode spaces"); layout.addWidget(self._nu)
        self._se = QCheckBox("Remove emoji"); layout.addWidget(self._se)
        self._sm = QCheckBox("Remove unicode marks (diacritics)"); layout.addWidget(self._sm)
        self._cc = QCheckBox("Split CamelCase (Camel Case)"); layout.addWidget(self._cc)

    def get_config(self):
        bk = []
        if self._cb1.isChecked(): bk.append("round")
        if self._cb2.isChecked(): bk.append("square")
        if self._cb3.isChecked(): bk.append("curly")
        return {"type": "CleanUp", "enabled": self.enabled(), "strip_brackets": bk,
                "replace_with_space": self._rws.text(), "fix_spaces": self._fs.isChecked(),
                "normalize_unicode": self._nu.isChecked(), "strip_emoji": self._se.isChecked(),
                "strip_marks": self._sm.isChecked(), "camel_case_split": self._cc.isChecked()}

    def _push_config(self, config):
        bk = config.get('strip_brackets', [])
        if hasattr(self, '_cb1'): self._cb1.setChecked('round' in bk)
        if hasattr(self, '_cb2'): self._cb2.setChecked('square' in bk)
        if hasattr(self, '_cb3'): self._cb3.setChecked('curly' in bk)
        if hasattr(self, '_rws'): self._rws.setText(config.get('replace_with_space', ''))
        if hasattr(self, '_fs'): self._fs.setChecked(config.get('fix_spaces', True))
        if hasattr(self, '_nu'): self._nu.setChecked(config.get('normalize_unicode', False))
        if hasattr(self, '_se'): self._se.setChecked(config.get('strip_emoji', False))
        if hasattr(self, '_sm'): self._sm.setChecked(config.get('strip_marks', False))
        if hasattr(self, '_cc'): self._cc.setChecked(config.get('camel_case_split', False))
