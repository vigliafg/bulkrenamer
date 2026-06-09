from renamer.rules.base import RenameRule
from PyQt6.QtWidgets import QVBoxLayout, QTextEdit, QLabel


class UserInputRule(RenameRule):
    name = "User Input"
    icon = "📋"
    rule_type = "UserInput"

    def default_config(self):
        return {"type": "UserInput", "enabled": True, "names": []}

    def _build_ui(self, layout: QVBoxLayout):
        layout.addWidget(QLabel("Lista nuovi nomi (uno per riga):"))
        self._text = QTextEdit()
        self._text.setPlaceholderText("nuovo_nome1.txt\nnuovo_nome2.txt\nnuovo_nome3.txt")
        layout.addWidget(self._text)

    def get_config(self):
        names = [line.strip() for line in self._text.toPlainText().strip().split("\n")
                 if line.strip()]
        return {"type": "UserInput", "enabled": self.enabled(), "names": names}

    def _push_config(self, config):
        if hasattr(self, '_text'):
            names = config.get('names', [])
            self._text.setPlainText("\n".join(names))
