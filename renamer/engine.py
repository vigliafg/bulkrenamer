"""Renaming engine. Pure logic, no GUI dependencies."""

import os
import re
import datetime
import random
from pathlib import Path
from typing import Any


def apply_rules_stack(
    filepath: str,
    rules_config: list[dict[str, Any]],
    index: int,
    total: int,
) -> str:
    """Apply a stack of rules to a single file's name."""
    stem = Path(filepath).stem
    ext = Path(filepath).suffix

    for cfg in rules_config:
        if not cfg.get("enabled", True):
            continue
        rule_type = cfg["type"]
        if rule_type == "Insert":
            stem = _apply_insert(stem, ext, filepath, cfg, index, total)
        elif rule_type == "Delete":
            stem = _apply_delete(stem, ext, cfg)
        elif rule_type == "Remove":
            stem = _apply_remove(stem, ext, cfg)
        elif rule_type == "Replace":
            stem = _apply_replace(stem, ext, cfg)
        elif rule_type == "Rearrange":
            stem = _apply_rearrange(stem, ext, filepath, cfg, index, total)
        elif rule_type == "Extension":
            ext = _apply_extension(ext, stem, cfg)
        elif rule_type == "Strip":
            stem = _apply_strip(stem, ext, cfg)
        elif rule_type == "Case":
            stem = _apply_case(stem, ext, cfg)
        elif rule_type == "Serialize":
            stem = _apply_serialize(stem, ext, cfg, index)
        elif rule_type == "Randomize":
            stem = _apply_randomize(stem, ext, cfg)
        elif rule_type == "Padding":
            stem = _apply_padding(stem, ext, cfg)
        elif rule_type == "CleanUp":
            stem = _apply_cleanup(stem, ext, cfg)
        elif rule_type == "Translit":
            stem = _apply_translit(stem, ext, cfg)
        elif rule_type == "ReformatDate":
            stem = _apply_reformat_date(stem, ext, cfg)
        elif rule_type == "Regex":
            stem = _apply_regex(stem, ext, cfg)
        elif rule_type == "UserInput":
            stem = _apply_user_input(stem, ext, index, cfg)
        elif rule_type == "Mapping":
            stem = _apply_mapping(stem, index, cfg)
    return stem + ext


# ── Meta tag expansion ────────────────────────────────────────────────────────

def _expand_meta(s: str, filepath: str, index: int, total: int) -> str:
    mt = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
    pad = len(str(total))
    toks = {
        "[[MTIME_DATE]]": mt.strftime("%Y%m%d"),
        "[[MTIME_YEAR]]": mt.strftime("%Y"),
        "[[MTIME_MONTH]]": mt.strftime("%m"),
        "[[MTIME_DAY]]": mt.strftime("%d"),
        "[[MTIME_TIME]]": mt.strftime("%H%M%S"),
        "[[INDEX]]": str(index + 1).zfill(pad),
        "[[INDEX0]]": str(index).zfill(pad),
    }
    for k, v in toks.items():
        s = s.replace(k, v)
    return s


# ── Individual rule implementations ──────────────────────────────────────────

def _skip_ext(stem: str, ext: str, cfg: dict, fn):
    """Apply fn to stem, then optionally skip extension."""
    return fn(stem)


def _apply_insert(stem, ext, filepath, cfg, index, total):
    text = _expand_meta(cfg.get("text", ""), filepath, index, total)
    where = cfg.get("where", "prefix")
    position = cfg.get("position", 1)
    after_text = cfg.get("after_text", "")
    before_text = cfg.get("before_text", "")
    skip_ext = cfg.get("skip_extension", False)
    target = stem
    if where == "prefix":
        return text + target
    elif where == "suffix":
        return target + text
    elif where == "position":
        pos = max(1, position) - 1
        return target[:pos] + text + target[pos:]
    elif where == "after_text":
        idx = target.find(after_text)
        if idx >= 0:
            return target[:idx + len(after_text)] + text + target[idx + len(after_text):]
        return target
    elif where == "before_text":
        idx = target.find(before_text)
        if idx >= 0:
            return target[:idx] + text + target[idx:]
        return target
    elif where == "replace":
        return text
    return target


def _apply_delete(stem, ext, cfg):
    mode_from = cfg.get("from_mode", "position")
    mode_until = cfg.get("until_mode", "count")
    from_val = cfg.get("from_val", 1)
    until_val = cfg.get("until_val", 0)
    skip_ext = cfg.get("skip_extension", False)
    rtl = cfg.get("rtl", False)
    keep_delims = cfg.get("keep_delimiters", False)
    target = stem

    # Determine start index
    if mode_from == "position":
        start = max(0, from_val - 1)
    elif mode_from == "delimiter":
        delim = cfg.get("from_delim", "")
        idx = target.find(delim)
        start = idx if idx >= 0 else 0
        if not keep_delims and idx >= 0:
            start = idx
    else:
        start = 0

    # Determine end index
    if mode_until == "count":
        end = start + max(0, until_val)
    elif mode_until == "delimiter":
        delim = cfg.get("until_delim", "")
        idx = target.find(delim, start + 1)
        end = idx + (0 if keep_delims else len(delim)) if idx >= 0 else len(target)
    elif mode_until == "end":
        end = len(target)
    else:
        end = start

    if cfg.get("delete_current_name", False):
        return ""
    return target[:start] + target[end:]


def _apply_remove(stem, ext, cfg):
    text = cfg.get("text", "")
    if not text:
        return stem
    occurrences = cfg.get("occurrences", "all")
    case_sensitive = cfg.get("case_sensitive", False)
    whole_words = cfg.get("whole_words", False)
    # Support multiple texts separated by *|*
    parts = text.split("*|*")
    result = stem
    for part in parts:
        if not part:
            continue
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.escape(part)
        if whole_words:
            pattern = r"\b" + pattern + r"\b"
        if occurrences == "first":
            result = re.sub(pattern, "", result, count=1, flags=flags)
        elif occurrences == "last":
            # Find the last occurrence
            matches = list(re.finditer(pattern, result, flags=flags))
            if matches:
                m = matches[-1]
                result = result[:m.start()] + result[m.end():]
        else:  # all
            result = re.sub(pattern, "", result, flags=flags)
    return result


def _apply_replace(stem, ext, cfg):
    find = cfg.get("find", "")
    if not find:
        return stem
    replace = cfg.get("replace", "")
    occurrences = cfg.get("occurrences", "all")
    case_sensitive = cfg.get("case_sensitive", False)
    whole_words = cfg.get("whole_words", False)
    use_wildcards = cfg.get("use_wildcards", False)
    use_regex = cfg.get("use_regex", False)

    # Support multiple find/replace with *|*
    find_parts = find.split("*|*")
    replace_parts = replace.split("*|*") if replace else [""] * len(find_parts)
    result = stem

    for f_part, r_part in zip(find_parts, replace_parts):
        if not f_part:
            continue
        if use_regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            count = 0 if occurrences == "all" else 1
            result = re.sub(f_part, r_part, result, count=count, flags=flags)
        else:
            pattern = f_part
            if use_wildcards:
                # Convert wildcards to regex
                pattern = re.escape(pattern)
                pattern = pattern.replace(r"\*", ".*").replace(r"\?", ".")
            else:
                pattern = re.escape(pattern)
            if whole_words:
                pattern = r"\b" + pattern + r"\b"
            flags = 0 if case_sensitive else re.IGNORECASE
            if occurrences == "first":
                result = re.sub(pattern, r_part, result, count=1, flags=flags)
            elif occurrences == "last":
                matches = list(re.finditer(pattern, result, flags=flags))
                if matches:
                    m = matches[-1]
                    result = result[:m.start()] + r_part + result[m.end():]
            else:
                result = re.sub(pattern, r_part, result, flags=flags)
    return result


def _apply_rearrange(stem, ext, filepath, cfg, index, total):
    split_using = cfg.get("split_using", "delimiters")
    delimiters = cfg.get("delimiters", " - ")
    positions_str = cfg.get("positions", "")
    new_pattern = cfg.get("new_pattern", "$1")
    skip_ext = cfg.get("skip_extension", False)
    rtl = cfg.get("rtl", False)

    # Split the name
    parts: list[str] = []
    if split_using == "delimiters":
        # Split by multiple delimiters separated by |
        dels = delimiters.split("|")
        # Build a regex from delimiters
        escaped = [re.escape(d) for d in dels]
        delim_re = "|".join(escaped)
        parts = re.split(delim_re, stem)
    elif split_using == "positions":
        # Split at exact positions
        poses = [int(p.strip()) for p in positions_str.split("|") if p.strip()]
        parts = []
        prev = 0
        for pos in sorted(poses):
            pos = max(1, pos) - 1
            if pos > prev:
                parts.append(stem[prev:pos])
            prev = pos
        parts.append(stem[prev:])
    else:
        # exact pattern - like delimiters but fixed order
        dels = delimiters.split("|")
        pattern = "^(.*?)" + "(.*?)".join(re.escape(d) for d in dels) + "(.*)$"
        m = re.match(pattern, stem)
        if m:
            parts = list(m.groups())
        else:
            parts = [stem]

    # Build new name
    result = _expand_meta(new_pattern, filepath, index, total)
    for i, p in enumerate(parts):
        result = result.replace(f"${i + 1}", p)
        result = result.replace(f"$-{len(parts) - i}", p)
    result = result.replace("$0", stem)
    return result


def _apply_extension(stem, ext, cfg):
    new_ext = cfg.get("new_extension", "")
    append_mode = cfg.get("append", False)
    remove_dup = cfg.get("remove_duplicates", False)
    case_sensitive = cfg.get("case_sensitive", False)

    if new_ext and not append_mode:
        ext = new_ext if new_ext.startswith(".") else "." + new_ext
    elif new_ext and append_mode:
        ext = ext + (new_ext if new_ext.startswith(".") else "." + new_ext)

    if remove_dup:
        # Remove duplicate consecutive extensions
        if ext:
            parts = ext.split(".")
            cleaned = []
            for p in parts:
                if not p:
                    continue
                if cleaned:
                    if case_sensitive:
                        if p != cleaned[-1]:
                            cleaned.append(p)
                    else:
                        if p.lower() != cleaned[-1].lower():
                            cleaned.append(p)
                else:
                    cleaned.append(p)
            ext = "." + ".".join(cleaned) if cleaned else ""
    return ext


def _apply_strip(stem, ext, cfg):
    chars = cfg.get("chars", "")
    sets = cfg.get("sets", [])  # list of predefined sets: digits, symbols, english, brackets
    positioning = cfg.get("positioning", "everywhere")
    invert = cfg.get("invert", False)
    case_sensitive = cfg.get("case_sensitive", False)

    remove_set = set(chars)
    for s in sets:
        if s == "digits":
            remove_set.update("0123456789")
        elif s == "symbols":
            remove_set.update("!\"#$%&'*+,-./:;=?@^_`|~")
        elif s == "english":
            remove_set.update("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
        elif s == "brackets":
            remove_set.update("(){}[]<>")

    if case_sensitive:
        # Remove both cases of letters in the set
        extra = set()
        for ch in list(remove_set):
            if ch.isalpha():
                if ch.islower():
                    extra.add(ch.upper())
                else:
                    extra.add(ch.lower())
        remove_set.update(extra)

    if invert:
        # Keep only the specified chars
        if positioning == "leading":
            i = 0
            while i < len(stem) and stem[i] in remove_set:
                i += 1
            return stem[i:]
        elif positioning == "trailing":
            i = len(stem) - 1
            while i >= 0 and stem[i] in remove_set:
                i -= 1
            return stem[:i + 1]
        else:
            return "".join(ch for ch in stem if ch in remove_set)
    else:
        if positioning == "leading":
            i = 0
            while i < len(stem) and stem[i] in remove_set:
                i += 1
            return stem[i:]
        elif positioning == "trailing":
            i = len(stem) - 1
            while i >= 0 and stem[i] in remove_set:
                i -= 1
            return stem[:i + 1]
        else:
            return "".join(ch for ch in stem if ch not in remove_set)


def _apply_case(stem, ext, cfg):
    mode = cfg.get("case_mode", "none")
    force_fragments = cfg.get("force_fragments", "")
    skip_ext = cfg.get("skip_extension", False)

    if mode == "lowercase":
        stem = stem.lower()
    elif mode == "uppercase":
        stem = stem.upper()
    elif mode == "title":
        stem = stem.title()
    elif mode == "invert":
        stem = "".join(ch.lower() if ch.isupper() else ch.upper() for ch in stem)
    elif mode == "first_capital":
        stem = stem[:1].upper() + stem[1:].lower() if stem else stem
    elif mode == "sentence":
        # Basic sentence case
        result = []
        caps_next = True
        for ch in stem:
            if caps_next and ch.isalpha():
                result.append(ch.upper())
                caps_next = False
            else:
                result.append(ch.lower())
                if ch in ".!?":
                    caps_next = True
        stem = "".join(result)

    # Force case for specific fragments
    if force_fragments:
        fragments = [f.strip() for f in force_fragments.split(",") if f.strip()]
        for frag in fragments:
            # Case-sensitive replacement
            stem = stem.replace(frag.lower(), frag)
            stem = stem.replace(frag.upper(), frag)

    return stem


def _apply_serialize(stem, ext, cfg, index):
    start = cfg.get("index_start", 1)
    step = cfg.get("step", 1)
    repeat = cfg.get("repeat", 1)
    reset_every = cfg.get("reset_every", 0)
    padding = cfg.get("pad_to_length", 0)
    where = cfg.get("where", "suffix")
    sep = cfg.get("separator", "_")
    system = cfg.get("numbering_system", "decimal")

    # Calculate index with repeat
    effective_idx = start + (index // repeat) * step

    # Build the serial number
    if system == "roman":
        num = _to_roman(max(1, effective_idx))
    elif system == "english_letters":
        num = _to_english_letters(max(1, effective_idx))
    elif system == "music_notes":
        num = _to_music_notes(max(1, effective_idx))
    else:  # decimal
        num = str(max(0, effective_idx))
        if padding > 0:
            num = num.zfill(padding)

    if where == "prefix":
        return num + sep + stem
    elif where == "suffix":
        return stem + sep + num
    elif where == "replace":
        return num
    return stem


def _to_roman(n: int) -> str:
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    sym = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    result = ""
    for v, s in zip(val, sym):
        while n >= v:
            result += s
            n -= v
    return result


def _to_english_letters(n: int) -> str:
    """Convert to base-26 using a-z then ba, bb, ..., zz, baa, ..."""
    if n < 1:
        return "a"
    result = []
    n -= 1
    while True:
        result.append(chr(ord('a') + (n % 26)))
        n = n // 26 - 1
        if n < 0:
            break
    return "".join(reversed(result))


def _to_music_notes(n: int) -> str:
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    n = max(0, n - 1)
    octave = n // 12
    note = n % 12
    return f"{notes[note]}{octave}"


def _apply_randomize(stem, ext, cfg):
    length = cfg.get("length", 8)
    chars = cfg.get("chars", "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    where = cfg.get("where", "suffix")
    sep = cfg.get("separator", "_")
    if not chars:
        return stem
    rand_str = "".join(random.choice(chars) for _ in range(length))
    if where == "prefix":
        return rand_str + sep + stem
    elif where == "suffix":
        return stem + sep + rand_str
    elif where == "replace":
        return rand_str
    return stem


def _apply_padding(stem, ext, cfg):
    mode = cfg.get("mode", "add_zero")
    if mode == "add_zero":
        length = cfg.get("length", 3)
        # Add zero padding to number sequences in the stem
        def _pad_num(m):
            num = m.group(0)
            return num.zfill(length) if len(num) < length else num
        result = re.sub(r"\d+", _pad_num, stem)
        return result
    elif mode == "remove_zero":
        # Remove leading zeros from number sequences
        def _unpad(m):
            return str(int(m.group(0))) if m.group(0).isdigit() else m.group(0)
        result = re.sub(r"\d+", _unpad, stem)
        return result
    elif mode == "text_padding":
        length = cfg.get("length", 10)
        pad_char = cfg.get("pad_char", " ")
        position = cfg.get("position", "left")
        pad_str = pad_char * max(0, length - len(stem))
        if position == "left":
            return pad_str + stem
        else:
            return stem + pad_str
    return stem


def _apply_cleanup(stem, ext, cfg):
    strip_brackets = cfg.get("strip_brackets", [])  # list: round, square, curly
    replace_with_space = cfg.get("replace_with_space", "")
    fix_spaces = cfg.get("fix_spaces", True)
    normalize_unicode = cfg.get("normalize_unicode", False)
    strip_emoji = cfg.get("strip_emoji", False)
    strip_marks = cfg.get("strip_marks", False)
    camel_case_split = cfg.get("camel_case_split", False)

    result = stem

    # Strip bracket content
    for bracket_type in strip_brackets:
        if bracket_type == "round":
            result = re.sub(r"\([^)]*\)", "", result)
        elif bracket_type == "square":
            result = re.sub(r"\[[^\]]*\]", "", result)
        elif bracket_type == "curly":
            result = re.sub(r"\{[^}]*\}", "", result)

    # Replace characters with spaces
    if replace_with_space:
        for ch in replace_with_space:
            result = result.replace(ch, " ")

    # Fix spaces
    if fix_spaces:
        result = re.sub(r"\s+", " ", result).strip()

    # Normalize unicode spaces
    if normalize_unicode:
        import unicodedata
        normalized = []
        for ch in result:
            if unicodedata.category(ch) == "Zs":
                normalized.append(" ")
            else:
                normalized.append(ch)
        result = "".join(normalized)

    # Strip emoji
    if strip_emoji:
        result = re.sub(r'[\U0001F300-\U0001F9FF\u2600-\u27BF\u2B50\u2700-\u27BF]', '', result)

    # Strip unicode marks (diacritics/combining marks)
    if strip_marks:
        import unicodedata
        result = "".join(ch for ch in unicodedata.normalize("NFD", result)
                         if unicodedata.category(ch) != "Mn")

    # CamelCase split
    if camel_case_split:
        result = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", result)

    return result


# ── Transliteration maps ─────────────────────────────────────────────────────

BUILTIN_TRANSLIT: dict[str, list[tuple[str, str]]] = {
    "German": [
        ("ä", "ae"), ("ö", "oe"), ("ü", "ue"),
        ("Ä", "Ae"), ("Ö", "Oe"), ("Ü", "Ue"), ("ß", "ss"),
    ],
    "French": [
        ("à", "a"), ("â", "a"), ("ç", "c"), ("é", "e"),
        ("è", "e"), ("ê", "e"), ("ë", "e"), ("î", "i"),
        ("ï", "i"), ("ô", "o"), ("ù", "u"), ("û", "u"),
        ("ü", "u"), ("ÿ", "y"), ("œ", "oe"), ("æ", "ae"),
    ],
    "Italian": [
        ("à", "a"), ("è", "e"), ("é", "e"), ("ì", "i"),
        ("ò", "o"), ("ù", "u"),
    ],
    "Spanish": [
        ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"),
        ("ú", "u"), ("ü", "u"), ("ñ", "n"), ("Ñ", "N"),
        ("¿", ""), ("¡", ""),
    ],
    "Portuguese": [
        ("á", "a"), ("à", "a"), ("â", "a"), ("ã", "a"),
        ("é", "e"), ("ê", "e"), ("í", "i"), ("ó", "o"),
        ("ô", "o"), ("õ", "o"), ("ú", "u"), ("ç", "c"),
    ],
    "Russian": [
        ("а", "a"), ("б", "b"), ("в", "v"), ("г", "g"),
        ("д", "d"), ("е", "e"), ("ё", "yo"), ("ж", "zh"),
        ("з", "z"), ("и", "i"), ("й", "y"), ("к", "k"),
        ("л", "l"), ("м", "m"), ("н", "n"), ("о", "o"),
        ("п", "p"), ("р", "r"), ("с", "s"), ("т", "t"),
        ("у", "u"), ("ф", "f"), ("х", "kh"), ("ц", "ts"),
        ("ч", "ch"), ("ш", "sh"), ("щ", "shch"), ("ъ", ""),
        ("ы", "y"), ("ь", ""), ("э", "e"), ("ю", "yu"), ("я", "ya"),
    ],
    "Greek": [
        ("α", "a"), ("β", "v"), ("γ", "g"), ("δ", "d"),
        ("ε", "e"), ("ζ", "z"), ("η", "i"), ("θ", "th"),
        ("ι", "i"), ("κ", "k"), ("λ", "l"), ("μ", "m"),
        ("ν", "n"), ("ξ", "x"), ("ο", "o"), ("π", "p"),
        ("ρ", "r"), ("σ", "s"), ("τ", "t"), ("υ", "y"),
        ("φ", "f"), ("χ", "ch"), ("ψ", "ps"), ("ω", "o"),
    ],
    "Japanese (Romaji)": [
        ("あ", "a"), ("い", "i"), ("う", "u"), ("え", "e"), ("お", "o"),
        ("か", "ka"), ("き", "ki"), ("く", "ku"), ("け", "ke"), ("こ", "ko"),
        ("さ", "sa"), ("し", "shi"), ("す", "su"), ("せ", "se"), ("そ", "so"),
        ("た", "ta"), ("ち", "chi"), ("つ", "tsu"), ("て", "te"), ("と", "to"),
        ("な", "na"), ("に", "ni"), ("ぬ", "nu"), ("ね", "ne"), ("の", "no"),
        ("は", "ha"), ("ひ", "hi"), ("ふ", "fu"), ("へ", "he"), ("ほ", "ho"),
        ("ま", "ma"), ("み", "mi"), ("む", "mu"), ("め", "me"), ("も", "mo"),
        ("や", "ya"), ("ゆ", "yu"), ("よ", "yo"),
        ("ら", "ra"), ("り", "ri"), ("る", "ru"), ("れ", "re"), ("ろ", "ro"),
        ("わ", "wa"), ("を", "wo"), ("ん", "n"),
    ],
    "Custom": [],
}


def _apply_translit(stem, ext, cfg):
    alphabet_name = cfg.get("alphabet", "")
    custom_map = cfg.get("custom_map", [])
    direction = cfg.get("direction", "forward")

    pairs: list[tuple[str, str]] = []
    if alphabet_name and alphabet_name in BUILTIN_TRANSLIT:
        pairs = list(BUILTIN_TRANSLIT[alphabet_name])
    if custom_map:
        pairs.extend(custom_map)
    if not pairs:
        return stem

    result = stem
    for src, dst in pairs:
        if direction == "backward":
            result = result.replace(dst, src)
        else:
            result = result.replace(src, dst)
    return result


def _apply_reformat_date(stem, ext, cfg):
    find_pattern = cfg.get("find_pattern", r"\d{4}-\d{2}-\d{2}")
    output_format = cfg.get("output_format", "%Y%m%d")
    try:
        # Try to find date matching the pattern
        m = re.search(find_pattern, stem)
        if m:
            date_str = m.group(0)
            # Try common input formats
            for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y", "%Y%m%d", "%d%m%Y", "%Y.%m.%d", "%d.%m.%Y"]:
                try:
                    dt = datetime.datetime.strptime(date_str, fmt)
                    new_date = dt.strftime(output_format)
                    stem = stem.replace(date_str, new_date, 1)
                    break
                except ValueError:
                    continue
    except Exception:
        pass
    return stem


def _apply_regex(stem, ext, cfg):
    pattern = cfg.get("pattern", "")
    replacement = cfg.get("replacement", "")
    count = cfg.get("count", 0)  # 0 = all
    if not pattern:
        return stem
    try:
        return re.sub(pattern, replacement, stem, count=count)
    except re.error:
        return stem


def _apply_user_input(stem, ext, index, cfg):
    names = cfg.get("names", [])
    if index < len(names):
        return names[index]
    return stem


def _apply_mapping(stem, index, cfg):
    mappings = cfg.get("mappings", {})  # dict of old_name -> new_name
    current = stem  # Note: this works on stem only; for full name mapping see below
    if current in mappings:
        return mappings[current]
    return stem

