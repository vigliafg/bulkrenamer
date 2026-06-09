from renamer.rules.base import RenameRule
from PyQt6.QtWidgets import QVBoxLayout, QTextEdit, QLabel


class MappingRule(RenameRule):
    name = "Mapping"
    icon = "🗺"
    rule_type = "Mapping"

    def default_config(self):
        return {"type": "Mapping", "enabled": True, "mappings": {}}

    def _build_ui(self, layout: QVBoxLayout):
        layout.addWidget(QLabel("Map old name = new name (one pair per line):"))
        self._text = QTextEdit()
        self._text.setPlaceholderText("old_name.txt = new_name.txt\nfile2.pdf = doc2.pdf")
        layout.addWidget(self._text)

    def get_config(self):
        mappings = {}
        for line in self._text.toPlainText().strip().split("\n"):
            line = line.strip()
            if "=" in line:
                parts = line.split("=", 1)
                if len(parts) == 2:
                    mappings[parts[0].strip()] = parts[1].strip()
        return {"type": "Mapping", "enabled": self.enabled(), "mappings": mappings}

    def _push_config(self, config):
        if hasattr(self, '_text'):
            mappings = config.get('mappings', {})
            text = "\n".join(f"{k} = {v}" for k, v in mappings.items())
            self._text.setPlainText(text)
