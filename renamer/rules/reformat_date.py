from renamer.rules.base import RenameRule
from PyQt6.QtWidgets import QVBoxLayout, QLineEdit, QLabel


class ReformatDateRule(RenameRule):
    name = "Reformat Date"
    icon = "📅"
    rule_type = "ReformatDate"

    def default_config(self):
        return {"type": "ReformatDate", "enabled": True,
                "find_pattern": r"\d{4}-\d{2}-\d{2}",
                "output_format": "%Y%m%d"}

    def _build_ui(self, layout: QVBoxLayout):
        layout.addWidget(QLabel("Regex pattern to find date:"))
        self._find = QLineEdit(); self._find.setText(r"\d{4}-\d{2}-\d{2}")
        layout.addWidget(self._find)

        layout.addWidget(QLabel("Output format (Python strftime):"))
        self._fmt = QLineEdit(); self._fmt.setText("%Y%m%d")
        layout.addWidget(self._fmt)

        layout.addWidget(QLabel(
            "Format examples: %Y=year, %m=month, %d=day, %H=hour, %M=minutes, %S=seconds"))
        layout.addWidget(QLabel(
            "Supported inputs: YYYY-MM-DD, DD-MM-YYYY, MM-DD-YYYY, YYYYMMDD, DDMMYYYY, YYYY.MM.DD, DD.MM.YYYY"))

    def get_config(self):
        return {"type": "ReformatDate", "enabled": self.enabled(),
                "find_pattern": self._find.text(),
                "output_format": self._fmt.text()}

    def _push_config(self, config):
        if hasattr(self, '_find'): self._find.setText(config.get('find_pattern', r'\d{4}-\d{2}-\d{2}'))
        if hasattr(self, '_fmt'): self._fmt.setText(config.get('output_format', '%Y%m%d'))
