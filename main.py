#!/usr/bin/env python3
"""Bulk File Renamer PRO — PyQt6 clone of ReNamer by den4b.com."""

import sys
from PyQt6.QtWidgets import QApplication
from renamer.app import BulkRenamerProApp


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Bulk File Renamer PRO")
    window = BulkRenamerProApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
