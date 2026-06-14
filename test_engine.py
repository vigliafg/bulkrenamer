"""Unit tests for the corrected engine functions."""

import re
import shutil
import sys
import os
import tempfile
import unittest
from pathlib import Path

# Allow importing from the parent package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from renamer.engine import (
    _apply_strip,
    _apply_mapping,
    _apply_user_input,
    _apply_delete,
    apply_rules_stack,
)


class TestApplyStrip(unittest.TestCase):
    """Tests for _apply_strip, focusing on the invert flag fix."""

    # ── Non-invert mode ──────────────────────────────────────────────────

    def test_non_invert_everywhere_removes_chars(self):
        cfg = {"chars": "abc", "positioning": "everywhere", "invert": False}
        result = _apply_strip("abcdef", cfg)
        self.assertEqual(result, "def")

    def test_non_invert_leading_strips_prefix_chars(self):
        cfg = {"chars": "0", "positioning": "leading", "invert": False}
        result = _apply_strip("000abc", cfg)
        self.assertEqual(result, "abc")

    def test_non_invert_leading_stops_at_non_matching(self):
        cfg = {"chars": "0", "positioning": "leading", "invert": False}
        result = _apply_strip("00a0b", cfg)
        self.assertEqual(result, "a0b")

    def test_non_invert_trailing_strips_suffix_chars(self):
        cfg = {"chars": "!", "positioning": "trailing", "invert": False}
        result = _apply_strip("hello!!!", cfg)
        self.assertEqual(result, "hello")

    def test_non_invert_trailing_stops_at_non_matching(self):
        cfg = {"chars": "!", "positioning": "trailing", "invert": False}
        result = _apply_strip("a!b!!", cfg)
        self.assertEqual(result, "a!b")

    # ── Invert mode (the bug fix) ────────────────────────────────────────

    def test_invert_everywhere_keeps_only_specified_chars(self):
        """Invert=True everywhere: keep ONLY chars in the set."""
        cfg = {"chars": "abc", "positioning": "everywhere", "invert": True}
        result = _apply_strip("abcdefxyzabc", cfg)
        self.assertEqual(result, "abcabc")

    def test_invert_leading_keeps_leading_matching_chars(self):
        """Invert=True leading: skip chars NOT in set, keep the rest."""
        cfg = {"chars": "0123456789", "positioning": "leading", "invert": True}
        result = _apply_strip("abc123", cfg)
        self.assertEqual(result, "123")

    def test_invert_leading_all_non_matching_returns_empty(self):
        """Invert+leading with NO matching chars: all chars are 'not in set', so all are stripped."""
        cfg = {"chars": "0", "positioning": "leading", "invert": True}
        result = _apply_strip("abcdef", cfg)
        self.assertEqual(result, "")

    def test_invert_leading_all_matching_returns_full_stem(self):
        cfg = {"chars": "0123", "positioning": "leading", "invert": True}
        result = _apply_strip("0123abc", cfg)
        self.assertEqual(result, "0123abc")

    def test_invert_trailing_keeps_trailing_matching_chars(self):
        """Invert=True trailing: skip trailing chars NOT in set, keep the rest."""
        cfg = {"chars": "0123456789", "positioning": "trailing", "invert": True}
        result = _apply_strip("123abc", cfg)
        self.assertEqual(result, "123")

    def test_invert_trailing_all_matching_returns_full_stem(self):
        cfg = {"chars": "abc123", "positioning": "trailing", "invert": True}
        result = _apply_strip("abc123", cfg)
        self.assertEqual(result, "abc123")

    def test_invert_trailing_all_non_matching_returns_empty(self):
        """Invert+trailing with NO matching chars: all chars are 'not in set', so all are stripped."""
        cfg = {"chars": "0", "positioning": "trailing", "invert": True}
        result = _apply_strip("abcdef", cfg)
        self.assertEqual(result, "")

    # ── Predefined sets ─────────────────────────────────────────────────

    def test_predefined_set_digits(self):
        cfg = {"sets": ["digits"], "positioning": "everywhere", "invert": False}
        result = _apply_strip("abc123def", cfg)
        self.assertEqual(result, "abcdef")

    def test_predefined_set_symbols(self):
        cfg = {"sets": ["symbols"], "positioning": "everywhere", "invert": False}
        result = _apply_strip("hello!@#world", cfg)
        self.assertEqual(result, "helloworld")

    def test_predefined_set_brackets(self):
        cfg = {"sets": ["brackets"], "positioning": "everywhere", "invert": False}
        result = _apply_strip("(hello)[world]{foo}", cfg)
        self.assertEqual(result, "helloworldfoo")

    # ── Case sensitive ──────────────────────────────────────────────────

    def test_case_sensitive_strips_both_cases(self):
        cfg = {"chars": "a", "positioning": "everywhere", "invert": False,
               "case_sensitive": True}
        result = _apply_strip("aAbBa", cfg)
        self.assertEqual(result, "bB")

    def test_case_insensitive_default(self):
        cfg = {"chars": "a", "positioning": "everywhere", "invert": False}
        result = _apply_strip("aAbBa", cfg)
        self.assertEqual(result, "AbB")

    # ── Edge cases ──────────────────────────────────────────────────────

    def test_empty_stem(self):
        cfg = {"chars": "abc", "positioning": "everywhere", "invert": False}
        result = _apply_strip("", cfg)
        self.assertEqual(result, "")

    def test_empty_chars_and_sets(self):
        cfg = {"chars": "", "sets": [], "positioning": "everywhere", "invert": False}
        result = _apply_strip("hello", cfg)
        self.assertEqual(result, "hello")

    def test_combined_sets_and_chars(self):
        cfg = {"chars": "x", "sets": ["digits"], "positioning": "everywhere",
               "invert": False}
        result = _apply_strip("a1b2x3c", cfg)
        self.assertEqual(result, "abc")


class TestApplyMapping(unittest.TestCase):
    """Tests for _apply_mapping, focusing on the full-name match fix."""

    def test_full_name_match_same_extension(self):
        cfg = {"mappings": {"file.txt": "renamed.txt"}}
        result = _apply_mapping("file", ".txt", 0, cfg)
        self.assertEqual(result, "renamed.txt")

    def test_full_name_match_different_extension(self):
        cfg = {"mappings": {"file.txt": "doc.pdf"}}
        result = _apply_mapping("file", ".txt", 0, cfg)
        self.assertEqual(result, "doc.pdf")

    def test_stem_only_fallback(self):
        cfg = {"mappings": {"file": "renamed"}}
        result = _apply_mapping("file", ".txt", 0, cfg)
        self.assertEqual(result, "renamed")

    def test_stem_only_fallback_with_extension(self):
        cfg = {"mappings": {"file": "renamed.pdf"}}
        result = _apply_mapping("file", ".txt", 0, cfg)
        self.assertEqual(result, "renamed.pdf")

    def test_full_name_takes_priority_over_stem(self):
        cfg = {"mappings": {
            "file": "stem_only",
            "file.txt": "full_match",
        }}
        result = _apply_mapping("file", ".txt", 0, cfg)
        self.assertEqual(result, "full_match")

    def test_no_match_returns_stem(self):
        cfg = {"mappings": {}}
        result = _apply_mapping("file", ".txt", 0, cfg)
        self.assertEqual(result, "file")

    def test_no_match_with_non_empty_mappings(self):
        cfg = {"mappings": {"other.txt": "renamed.txt"}}
        result = _apply_mapping("file", ".txt", 0, cfg)
        self.assertEqual(result, "file")

    def test_empty_mappings_dict(self):
        cfg = {}
        result = _apply_mapping("file", ".txt", 0, cfg)
        self.assertEqual(result, "file")

    def test_empty_extension(self):
        cfg = {"mappings": {"file": "renamed"}}
        result = _apply_mapping("file", "", 0, cfg)
        self.assertEqual(result, "renamed")

    def test_full_name_match_no_extension(self):
        cfg = {"mappings": {"README": "readme"}}
        result = _apply_mapping("README", "", 0, cfg)
        self.assertEqual(result, "readme")


class TestApplyMappingIntegration(unittest.TestCase):
    """Integration tests: apply_rules_stack with Mapping rule."""

    def test_full_name_mapping_splits_stem_and_ext(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test")
            tmp = f.name
        try:
            cfg = [{"type": "Mapping", "enabled": True,
                    "mappings": {os.path.basename(tmp): "renamed.md"}}]
            result = apply_rules_stack(tmp, cfg, 0, 1)
            self.assertEqual(result, "renamed.md")
        finally:
            os.unlink(tmp)

    def test_stem_only_mapping_preserves_extension(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test")
            tmp = f.name
        try:
            stem = os.path.basename(tmp).replace(".txt", "")
            cfg = [{"type": "Mapping", "enabled": True,
                    "mappings": {stem: "renamed"}}]
            result = apply_rules_stack(tmp, cfg, 0, 1)
            self.assertEqual(result, "renamed.txt")
        finally:
            os.unlink(tmp)

    def test_no_mapping_match_identity(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test")
            tmp = f.name
        try:
            cfg = [{"type": "Mapping", "enabled": True, "mappings": {}}]
            result = apply_rules_stack(tmp, cfg, 0, 1)
            self.assertEqual(result, os.path.basename(tmp))
        finally:
            os.unlink(tmp)


class TestApplyUserInput(unittest.TestCase):
    """Tests for _apply_user_input, focusing on the full-name split fix."""

    def test_returns_name_at_index(self):
        cfg = {"names": ["alpha", "beta", "gamma"]}
        result = _apply_user_input("old", "", 1, cfg)
        self.assertEqual(result, "beta")

    def test_index_out_of_range_returns_stem(self):
        cfg = {"names": ["alpha"]}
        result = _apply_user_input("original", "", 5, cfg)
        self.assertEqual(result, "original")

    def test_empty_names_returns_stem(self):
        cfg = {"names": []}
        result = _apply_user_input("original", "", 0, cfg)
        self.assertEqual(result, "original")

    def test_returns_full_name_with_extension(self):
        cfg = {"names": ["renamed.pdf", "file.md"]}
        result = _apply_user_input("old.txt", ".txt", 0, cfg)
        self.assertEqual(result, "renamed.pdf")


class TestApplyUserInputIntegration(unittest.TestCase):
    """Integration tests: apply_rules_stack with UserInput rule."""

    def test_user_input_splits_stem_and_ext(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test")
            tmp = f.name
        try:
            cfg = [{"type": "UserInput", "enabled": True,
                    "names": ["renamed.md"]}]
            result = apply_rules_stack(tmp, cfg, 0, 1)
            self.assertEqual(result, "renamed.md")
        finally:
            os.unlink(tmp)

    def test_user_input_without_extension_preserves_original_ext(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"test")
            tmp = f.name
        try:
            cfg = [{"type": "UserInput", "enabled": True,
                    "names": ["renamed"]}]
            result = apply_rules_stack(tmp, cfg, 0, 1)
            self.assertEqual(result, "renamed.pdf")
        finally:
            os.unlink(tmp)

    def test_user_input_index_out_of_range_identity(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test")
            tmp = f.name
        try:
            cfg = [{"type": "UserInput", "enabled": True,
                    "names": []}]
            result = apply_rules_stack(tmp, cfg, 0, 1)
            self.assertEqual(result, os.path.basename(tmp))
        finally:
            os.unlink(tmp)


class TestApplyDelete(unittest.TestCase):
    """Tests for _apply_delete, focusing on the keep_delimiters fix."""

    # ── Position-based from/until ────────────────────────────────────────

    def test_delete_count_from_position(self):
        cfg = {"from_mode": "position", "from_val": 2,
               "until_mode": "count", "until_val": 3}
        result = _apply_delete("abcdefgh", "", cfg)
        self.assertEqual(result, "aefgh")

    def test_delete_from_position_to_end(self):
        cfg = {"from_mode": "position", "from_val": 4,
               "until_mode": "end"}
        result = _apply_delete("abcdef", "", cfg)
        self.assertEqual(result, "abc")

    # ── Delimiter from: keep_delimiters=True (the fix) ───────────────────

    def test_from_delim_keep_delimiters_true(self):
        cfg = {"from_mode": "delimiter", "from_delim": " - ",
               "until_mode": "end", "keep_delimiters": True}
        result = _apply_delete("prefix - suffix", "", cfg)
        self.assertEqual(result, "prefix - ")

    def test_from_delim_keep_delimiters_false(self):
        cfg = {"from_mode": "delimiter", "from_delim": " - ",
               "until_mode": "end", "keep_delimiters": False}
        result = _apply_delete("prefix - suffix", "", cfg)
        self.assertEqual(result, "prefix")

    def test_from_delim_keep_delimiters_true_count(self):
        cfg = {"from_mode": "delimiter", "from_delim": " - ",
               "until_mode": "count", "until_val": 3,
               "keep_delimiters": True}
        result = _apply_delete("foo - bar", "", cfg)
        self.assertEqual(result, "foo - ")

    def test_from_delim_keep_delimiters_false_count(self):
        cfg = {"from_mode": "delimiter", "from_delim": " - ",
               "until_mode": "count", "until_val": 3,
               "keep_delimiters": False}
        result = _apply_delete("foo - bar", "", cfg)
        self.assertEqual(result, "foobar")

    # ── Delimiter until ──────────────────────────────────────────────────

    def test_until_delim_keep_delimiters_true(self):
        cfg = {"from_mode": "position", "from_val": 1,
               "until_mode": "delimiter", "until_delim": " - ",
               "keep_delimiters": True}
        result = _apply_delete("abc - xyz", "", cfg)
        self.assertEqual(result, " - xyz")

    def test_until_delim_keep_delimiters_false(self):
        cfg = {"from_mode": "position", "from_val": 1,
               "until_mode": "delimiter", "until_delim": " - ",
               "keep_delimiters": False}
        result = _apply_delete("abc - xyz", "", cfg)
        self.assertEqual(result, "xyz")

    # ── Both delimiters with keep_delimiters ─────────────────────────────

    def test_both_delims_keep_true(self):
        cfg = {"from_mode": "delimiter", "from_delim": "[",
               "until_mode": "delimiter", "until_delim": "]",
               "keep_delimiters": True}
        result = _apply_delete("pre[inner]post", "", cfg)
        self.assertEqual(result, "pre[]post")

    def test_both_delims_keep_false(self):
        cfg = {"from_mode": "delimiter", "from_delim": "[",
               "until_mode": "delimiter", "until_delim": "]",
               "keep_delimiters": False}
        result = _apply_delete("pre[inner]post", "", cfg)
        self.assertEqual(result, "prepost")

    # ── Edge cases ──────────────────────────────────────────────────────

    def test_delete_current_name(self):
        cfg = {"delete_current_name": True}
        result = _apply_delete("any_name", "", cfg)
        self.assertEqual(result, "")

    def test_delimiter_not_found(self):
        cfg = {"from_mode": "delimiter", "from_delim": "XYZ",
               "until_mode": "end"}
        result = _apply_delete("abcdef", "", cfg)
        self.assertEqual(result, "")

    def test_empty_delimiter(self):
        cfg = {"from_mode": "delimiter", "from_delim": "",
               "until_mode": "end", "keep_delimiters": False}
        result = _apply_delete("abcdef", "", cfg)
        self.assertEqual(result, "")


class TestApplyRulesStackEndToEnd(unittest.TestCase):
    """End-to-end tests for apply_rules_stack: combinations, ordering, disabled rules."""

    def _make_temp(self, name="testfile.txt"):
        """Create a temp file with an EXPLICIT known name (platform-independent)."""
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        fpath = os.path.join(d, name)
        Path(fpath).write_text("test")
        return fpath

    def _cfg(self, rule_type, enabled=True, **kwargs):
        cfg = {"type": rule_type, "enabled": enabled}
        cfg.update(kwargs)
        return cfg

    # ── Single rule identity ─────────────────────────────────────────────

    def test_empty_rules_returns_original_name(self):
        tmp = self._make_temp("myfile.txt")
        result = apply_rules_stack(tmp, [], 0, 1)
        self.assertEqual(result, "myfile.txt")

    def test_all_disabled_rules_identity(self):
        tmp = self._make_temp("myfile.txt")
        cfg = [
            self._cfg("Replace", enabled=False, find="x", replace="y"),
            self._cfg("Case", enabled=False, case_mode="uppercase"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "myfile.txt")

    # ── Rule combinations ────────────────────────────────────────────────

    def test_replace_then_case(self):
        """Replace text, then change case."""
        tmp = self._make_temp("report_final.txt")
        cfg = [
            self._cfg("Replace", find="report", replace="hello_world"),
            self._cfg("Case", case_mode="title"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "Hello_World_Final.txt")

    def test_case_then_replace(self):
        """Change case then replace — different result from replace-then-case."""
        tmp = self._make_temp("doc_abc.txt")
        cfg = [
            self._cfg("Case", case_mode="uppercase"),
            self._cfg("Replace", find="ABC", replace="final"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "DOC_final.txt")

    def test_strip_then_padding(self):
        tmp = self._make_temp("hello.txt")
        cfg = [
            self._cfg("Strip", chars="aeiou", positioning="everywhere"),
            self._cfg("Padding", mode="text_padding", length=10,
                      pad_char="_", position="left"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "_______hll.txt")

    def test_serialize_then_insert(self):
        """Add serial number, then insert prefix."""
        tmp = self._make_temp("photo.txt")
        cfg = [
            self._cfg("Serialize", index_start=10, step=5, pad_to_length=3,
                      where="prefix", separator="-"),
            self._cfg("Insert", text="IMG_", where="prefix"),
        ]
        result = apply_rules_stack(tmp, cfg, 2, 10)
        self.assertEqual(result, "IMG_020-photo.txt")

    # ── Extension changes in combination ─────────────────────────────────

    def test_extension_then_replace(self):
        """Change extension first, then modify stem."""
        tmp = self._make_temp("notes_tmp.txt")
        cfg = [
            self._cfg("Extension", new_extension="md"),
            self._cfg("Replace", find="_tmp", replace=""),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "notes.md")

    def test_replace_then_extension(self):
        """Modify stem first, then change extension."""
        tmp = self._make_temp("notes_tmp.txt")
        cfg = [
            self._cfg("Replace", find="_tmp", replace=""),
            self._cfg("Extension", new_extension="md"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "notes.md")

    # ── Mapping + other rules (stem/ext split behavior) ──────────────────

    def test_mapping_then_case(self):
        """Mapping splits stem/ext correctly before next rule modifies stem."""
        tmp = self._make_temp("Original.txt")
        cfg = [
            self._cfg("Mapping", mappings={"Original.txt": "Changed.MD"}),
            self._cfg("Case", case_mode="lowercase"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "changed.MD")

    def test_case_then_mapping(self):
        """Case before mapping — mapping matches the modified stem."""
        tmp = self._make_temp("file.txt")
        cfg = [
            self._cfg("Case", case_mode="uppercase"),
            self._cfg("Mapping", mappings={"FILE.txt": "final.pdf"}),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "final.pdf")

    def test_user_input_then_replace(self):
        """UserInput renames, then Replace works on the new stem."""
        tmp = self._make_temp("old.txt")
        cfg = [
            self._cfg("UserInput", names=["report_2025.txt"]),
            self._cfg("Replace", find="_", replace="-"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "report-2025.txt")

    # ── Disabled rules ───────────────────────────────────────────────────

    def test_disabled_rule_skipped(self):
        """A disabled rule in the middle is skipped."""
        tmp = self._make_temp("hello.txt")
        cfg = [
            self._cfg("Case", case_mode="uppercase"),
            self._cfg("Strip", enabled=False, chars="HL", positioning="everywhere"),
            self._cfg("Insert", text="PREFIX_", where="prefix"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "PREFIX_HELLO.txt")

    def test_only_disabled_rules_identity(self):
        tmp = self._make_temp("myfile.txt")
        cfg = [
            self._cfg("Case", enabled=False, case_mode="uppercase"),
            self._cfg("Strip", enabled=False, chars="aeiou"),
            self._cfg("Replace", enabled=False, find="x", replace="y"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "myfile.txt")

    # ── Rule ordering matters ────────────────────────────────────────────

    def test_order_strip_before_replace_affects_result(self):
        """Strip then Replace: strip removes chars, then replace on remainder."""
        tmp = self._make_temp("hello.txt")
        cfg = [
            self._cfg("Strip", chars="hl", positioning="everywhere"),
            self._cfg("Replace", find="eo", replace="A"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "A.txt")

    def test_order_replace_before_strip_different_result(self):
        """Replace then Strip: replace first, then strip from the result."""
        tmp = self._make_temp("hello.txt")
        cfg = [
            self._cfg("Replace", find="llo", replace="XX"),
            self._cfg("Strip", chars="X", positioning="everywhere"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "he.txt")

    # ── Multi-rule pipeline ──────────────────────────────────────────────

    def test_full_pipeline_five_rules(self):
        """Five rules applied in sequence."""
        tmp = self._make_temp("Report_Draft_v2.txt")
        cfg = [
            self._cfg("Case", case_mode="lowercase"),
            self._cfg("Strip", chars="0123456789", positioning="everywhere"),
            self._cfg("Replace", find="report", replace="final"),
            self._cfg("Insert", text="[", where="prefix"),
            self._cfg("Insert", text="]", where="suffix"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "[final_draft_v].txt")

    def test_full_pipeline_with_extension_change(self):
        """Extension change mid-pipeline, subsequent rules see new ext."""
        tmp = self._make_temp("readme.txt")
        cfg = [
            self._cfg("Extension", new_extension="md"),
            self._cfg("Insert", text="docs/", where="prefix"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "docs/readme.md")

    # ── Meta tokens in Insert ────────────────────────────────────────────

    def test_insert_with_index_token(self):
        tmp = self._make_temp("item.txt")
        cfg = [
            self._cfg("Insert", text="[[INDEX]]_", where="prefix"),
        ]
        result = apply_rules_stack(tmp, cfg, 4, 10)
        self.assertEqual(result, "05_item.txt")

    def test_insert_with_index0_token(self):
        tmp = self._make_temp("item.txt")
        cfg = [
            self._cfg("Insert", text="[[INDEX0]]_", where="prefix"),
        ]
        result = apply_rules_stack(tmp, cfg, 4, 100)
        self.assertEqual(result, "004_item.txt")

    # ── Cleanup + spacing ────────────────────────────────────────────────

    def test_cleanup_then_case(self):
        tmp = self._make_temp("myFile.txt")
        cfg = [
            self._cfg("CleanUp", fix_spaces=True, camel_case_split=True),
            self._cfg("Case", case_mode="title"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "My File.txt")

    # ── Regex rule ───────────────────────────────────────────────────────

    def test_regex_rule_basic(self):
        tmp = self._make_temp("document.txt")
        cfg = [
            self._cfg("Regex", pattern=r"^doc", replacement="file"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "fileument.txt")

    def test_regex_with_case(self):
        tmp = self._make_temp("abc.txt")
        cfg = [
            self._cfg("Regex", pattern=r".+", replacement="FINAL"),
            self._cfg("Case", case_mode="lowercase"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "final.txt")

    # ── Randomize (test for non-empty / correct structure) ───────────────

    def test_randomize_suffix_structure(self):
        tmp = self._make_temp("doc.txt")
        cfg = [
            self._cfg("Randomize", length=10, where="suffix", separator="_"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertTrue(result.startswith("doc_"))
        self.assertTrue(result.endswith(".txt"))
        body = result[4:-4]
        self.assertEqual(len(body), 10)
        self.assertTrue(all(c.isalnum() for c in body))

    # ── Translit ─────────────────────────────────────────────────────────

    def test_translit_italian_forward(self):
        """Italian transliteration: accented chars become ASCII equivalents."""
        tmp = self._make_temp("citta.txt")
        cfg = [
            self._cfg("Translit", alphabet="Italian", direction="forward"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "citta.txt")

    # ── Remove rule ──────────────────────────────────────────────────────

    def test_remove_multiple_texts(self):
        tmp = self._make_temp("aXbYc.txt")
        cfg = [
            self._cfg("Remove", text="X*|*Y", occurrences="all"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "abc.txt")

    # ── Delete rule in pipeline ──────────────────────────────────────────

    def test_delete_then_insert(self):
        tmp = self._make_temp("prefixABC.txt")
        cfg = [
            self._cfg("Delete", from_mode="position", from_val=1,
                      until_mode="count", until_val=6),
            self._cfg("Insert", text="NEW", where="prefix"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "NEWABC.txt")

    def test_delete_with_delimiters_keep_true(self):
        """Delete with from/until delimiters, keep_delimiters=True."""
        tmp = self._make_temp("pre[inner]post.txt")
        cfg = [
            self._cfg("Delete", from_mode="delimiter", from_delim="[",
                      until_mode="delimiter", until_delim="]",
                      keep_delimiters=True),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "pre[]post.txt")

    def test_delete_with_delimiters_keep_false(self):
        """Delete with from/until delimiters, keep_delimiters=False."""
        tmp = self._make_temp("pre[inner]post.txt")
        cfg = [
            self._cfg("Delete", from_mode="delimiter", from_delim="[",
                      until_mode="delimiter", until_delim="]",
                      keep_delimiters=False),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "prepost.txt")

    # ── Rearrange rule ───────────────────────────────────────────────────

    def test_rearrange_with_delimiters(self):
        """Split by delimiter and rearrange parts."""
        tmp = self._make_temp("Report - 2025 - Q1.txt")
        cfg = [
            self._cfg("Rearrange", split_using="delimiters",
                      delimiters=" - ", new_pattern="$3 - $1 - $2"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "Q1 - Report - 2025.txt")

    def test_rearrange_with_positions(self):
        """Split at exact character positions and rearrange."""
        tmp = self._make_temp("20250614_report.txt")
        cfg = [
            self._cfg("Rearrange", split_using="positions",
                      positions="9", new_pattern="$2-$1"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "_report-20250614.txt")

    def test_rearrange_simple_swap(self):
        """Simple two-part swap with delimiter."""
        tmp = self._make_temp("author_title.txt")
        cfg = [
            self._cfg("Rearrange", split_using="delimiters",
                      delimiters="_", new_pattern="$2_$1"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "title_author.txt")

    # ── ReformatDate rule ────────────────────────────────────────────────

    def test_reformat_date_yyyy_mm_dd_to_yyyymmdd(self):
        """Reformat YYYY-MM-DD date inside filename to YYYYMMDD."""
        tmp = self._make_temp("photo_2025-06-14.txt")
        cfg = [
            self._cfg("ReformatDate", find_pattern=r"\d{4}-\d{2}-\d{2}",
                      output_format="%Y%m%d"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "photo_20250614.txt")

    def test_reformat_date_dd_mm_yyyy_to_yyyymmdd(self):
        """Reformat DD-MM-YYYY date to YYYYMMDD."""
        tmp = self._make_temp("log_14-06-2025.txt")
        cfg = [
            self._cfg("ReformatDate", find_pattern=r"\d{2}-\d{2}-\d{4}",
                      output_format="%Y%m%d"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "log_20250614.txt")

    def test_reformat_date_not_found_identity(self):
        """No date pattern found → filename unchanged."""
        tmp = self._make_temp("no_date_here.txt")
        cfg = [
            self._cfg("ReformatDate", find_pattern=r"\d{4}-\d{2}-\d{2}",
                      output_format="%Y%m%d"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "no_date_here.txt")

    # ── Insert with after_text / before_text ─────────────────────────────

    def test_insert_after_text(self):
        """Insert text after a specific substring."""
        tmp = self._make_temp("hello_world.txt")
        cfg = [
            self._cfg("Insert", text="_done", where="after_text",
                      after_text="hello"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "hello_done_world.txt")

    def test_insert_before_text(self):
        """Insert text before a specific substring."""
        tmp = self._make_temp("hello_world.txt")
        cfg = [
            self._cfg("Insert", text="pre_", where="before_text",
                      before_text="world"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "hello_pre_world.txt")

    def test_insert_after_text_not_found_returns_unchanged(self):
        """Insert after_text not found → stem returned unchanged."""
        tmp = self._make_temp("hello.txt")
        cfg = [
            self._cfg("Insert", text="_done", where="after_text",
                      after_text="XYZ"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "hello.txt")

    # ── Padding add_zero / remove_zero ───────────────────────────────────

    def test_padding_add_zero(self):
        """Pad numbers in filename to a fixed width."""
        tmp = self._make_temp("file5_img3.txt")
        cfg = [
            self._cfg("Padding", mode="add_zero", length=4),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "file0005_img0003.txt")

    def test_padding_add_zero_already_padded(self):
        """Numbers already at or above padding width are left unchanged."""
        tmp = self._make_temp("file00005.txt")
        cfg = [
            self._cfg("Padding", mode="add_zero", length=3),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "file00005.txt")

    def test_padding_remove_zero(self):
        """Remove leading zeros from numbers."""
        tmp = self._make_temp("file0005_img0003.txt")
        cfg = [
            self._cfg("Padding", mode="remove_zero"),
        ]
        result = apply_rules_stack(tmp, cfg, 0, 1)
        self.assertEqual(result, "file5_img3.txt")


if __name__ == "__main__":
    unittest.main()
