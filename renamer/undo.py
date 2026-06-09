"""Undo/Redo manager for file rename operations."""

import os
from typing import Optional


class UndoManager:
    """Stores rename operations as (old_path, new_path) pairs for undo."""

    def __init__(self) -> None:
        self._stack: list[list[tuple[str, str]]] = []

    def push(self, operations: list[tuple[str, str]]) -> None:
        """Push a batch of (old_path, new_path) pairs onto the undo stack."""
        if operations:
            self._stack.append(operations)

    def pop(self) -> list[tuple[str, str]]:
        """Pop the last batch of operations."""
        if self._stack:
            return self._stack.pop()
        return []

    def can_undo(self) -> bool:
        return len(self._stack) > 0

    def clear(self) -> None:
        self._stack.clear()

    def undo_last(self, file_list: list[str]) -> tuple[int, list[str]]:
        """Undo the last batch. Returns (restored_count, error_messages)."""
        if not self._stack:
            return 0, ["No operation to undo."]

        last = self._stack.pop()
        restored = 0
        errors: list[str] = []
        for old_fp, new_fp in reversed(last):
            try:
                if not os.path.exists(new_fp):
                    errors.append(f"{os.path.basename(new_fp)}: file not found")
                    continue
                os.rename(new_fp, old_fp)
                if new_fp in file_list:
                    file_list[file_list.index(new_fp)] = old_fp
                restored += 1
            except Exception as e:
                errors.append(f"{os.path.basename(new_fp)}: {e}")
        return restored, errors
