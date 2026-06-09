from renamer.rules.base import RenameRule
from PyQt6.QtWidgets import QVBoxLayout, QLineEdit, QLabel, QCheckBox


class ExtensionRule(RenameRule):
    name = "Extension"
    icon = "🔧"
    rule_type = "Extension"

    def default_config(self):
        return {"type": "Extension", "enabled": True, "new_extension": "",
                "append": False, "remove_duplicates": False, "case_sensitive": False}

    def _build_ui(self, layout: QVBoxLayout):
        layout.addWidget(QLabel("Nuova estensione (senza punto):"))
        self._ext = QLineEdit()
        self._ext.setPlaceholderText("es: txt, mp3, jpg")
        layout.addWidget(self._ext)

        self._append = QCheckBox("Aggiungi al nome originale (non sostituire)")
        layout.addWidget(self._append)
        self._rmdup = QCheckBox("Rimuovi estensioni duplicate")
        layout.addWidget(self._rmdup)
        self._cs = QCheckBox("Case sensitive (per duplicati)")
        layout.addWidget(self._cs)

    def get_config(self):
        return {"type": "Extension", "enabled": self.enabled(), "new_extension": self._ext.text(),
                "append": self._append.isChecked(), "remove_duplicates": self._rmdup.isChecked(),
                "case_sensitive": self._cs.isChecked()}

    def _push_config(self, config):
        if hasattr(self, '_ext'): self._ext.setText(config.get('new_extension', ''))
        if hasattr(self, '_append'): self._append.setChecked(config.get('append', False))
        if hasattr(self, '_rmdup'): self._rmdup.setChecked(config.get('remove_duplicates', False))
        if hasattr(self, '_cs'): self._cs.setChecked(config.get('case_sensitive', False))
