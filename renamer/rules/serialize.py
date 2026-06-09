from renamer.rules.base import RenameRule
from PyQt6.QtWidgets import QVBoxLayout, QComboBox, QSpinBox, QLabel, QCheckBox, QLineEdit


class SerializeRule(RenameRule):
    name = "Serialize"
    icon = "🔢"
    rule_type = "Serialize"

    def default_config(self):
        return {"type": "Serialize", "enabled": True, "index_start": 1, "step": 1,
                "repeat": 1, "reset_every": 0, "pad_to_length": 0,
                "where": "suffix", "separator": "_", "numbering_system": "decimal"}

    def _build_ui(self, layout: QVBoxLayout):
        layout.addWidget(QLabel("Numbering system:"))
        self._sys = QComboBox()
        self._sys.addItems(["decimal", "roman", "english_letters", "music_notes"])
        layout.addWidget(self._sys)

        layout.addWidget(QLabel("Start index:"))
        self._start = QSpinBox(); self._start.setRange(0, 99999); self._start.setValue(1)
        layout.addWidget(self._start)

        layout.addWidget(QLabel("Step:"))
        self._step = QSpinBox(); self._step.setRange(-9999, 9999); self._step.setValue(1)
        layout.addWidget(self._step)

        layout.addWidget(QLabel("Repeat (same index for N files):"))
        self._repeat = QSpinBox(); self._repeat.setRange(1, 9999); self._repeat.setValue(1)
        layout.addWidget(self._repeat)

        layout.addWidget(QLabel("Zero-pad to length (0=off):"))
        self._pad = QSpinBox(); self._pad.setRange(0, 20); self._pad.setValue(0)
        layout.addWidget(self._pad)

        layout.addWidget(QLabel("Where:"))
        self._where = QComboBox(); self._where.addItems(["suffix", "prefix", "replace"])
        layout.addWidget(self._where)

        layout.addWidget(QLabel("Separator:"))
        self._sep = QLineEdit(); self._sep.setText("_")
        layout.addWidget(self._sep)

    def get_config(self):
        return {"type": "Serialize", "enabled": self.enabled(),
                "numbering_system": self._sys.currentText(), "index_start": self._start.value(),
                "step": self._step.value(), "repeat": self._repeat.value(),
                "pad_to_length": self._pad.value(), "where": self._where.currentText(),
                "separator": self._sep.text()}

    def _push_config(self, config):
        if hasattr(self, '_sys'):
            idx = self._sys.findText(config.get('numbering_system', 'decimal'))
            if idx >= 0: self._sys.setCurrentIndex(idx)
        if hasattr(self, '_start'): self._start.setValue(config.get('index_start', 1))
        if hasattr(self, '_step'): self._step.setValue(config.get('step', 1))
        if hasattr(self, '_repeat'): self._repeat.setValue(config.get('repeat', 1))
        if hasattr(self, '_pad'): self._pad.setValue(config.get('pad_to_length', 0))
        if hasattr(self, '_where'):
            idx = self._where.findText(config.get('where', 'suffix'))
            if idx >= 0: self._where.setCurrentIndex(idx)
        if hasattr(self, '_sep'): self._sep.setText(config.get('separator', '_'))
