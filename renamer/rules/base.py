"""Base class for all rename rules."""

from __future__ import annotations
from typing import Any
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QGroupBox


class RuleResult:
    """Result of a rule configuration dialog."""

    def __init__(self, accepted: bool, config: dict[str, Any] | None = None) -> None:
        self.accepted = accepted
        self.config: dict[str, Any] = config or {"type": "", "enabled": True}


class RenameRule:
    """Base class for a rename rule with config dialog."""

    name: str = ""
    icon: str = ""   # emoji
    rule_type: str = ""

    def __init__(self) -> None:
        self._config: dict[str, Any] = {"type": self.rule_type, "enabled": True}
        self._widget: QWidget | None = None

    def default_config(self) -> dict[str, Any]:
        return {"type": self.rule_type, "enabled": True}

    def build_widget(self, parent: QWidget | None = None) -> QWidget:
        """Build and return the configuration widget for this rule."""
        w = QWidget(parent)
        w.setObjectName(f"rule_{self.rule_type}")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self._build_ui(layout)
        self._widget = w
        return w

    def _build_ui(self, layout: QVBoxLayout) -> None:
        """Override in subclasses to build the UI."""
        raise NotImplementedError

    def set_config(self, config: dict[str, Any]) -> None:
        """Load config into the UI. Subclasses can override _push_config to update widgets."""
        self._config = config
        if self._widget is not None:
            self._push_config(config)

    def _push_config(self, config: dict[str, Any]) -> None:
        """Override in subclasses to push config values into UI widgets."""
        pass

    def get_config(self) -> dict[str, Any]:
        """Get current config from the UI."""
        return self._config

    def widget(self) -> QWidget | None:
        return self._widget

    def enabled(self) -> bool:
        return self._config.get("enabled", True)

    def set_enabled(self, val: bool) -> None:
        self._config["enabled"] = val
