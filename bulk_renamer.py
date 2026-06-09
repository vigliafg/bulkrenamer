#!/usr/bin/env python3
"""
Bulk File Renamer — GUI customtkinter
Funzionalità: trova/sostituisci (testo e regex), riordina token,
prefisso/suffisso con token data/EXIF, numerazione sequenziale,
cambio estensione, case conversion, undo illimitato, preview live.

Dipendenze:
    pip install customtkinter
"""

import os
import re
import datetime
import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pathlib import Path

import customtkinter as ctk

# ── tema ──────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# palette Catppuccin Mocha
C = dict(
    base    = "#1e1e2e",
    mantle  = "#181825",
    surface0= "#313244",
    surface1= "#45475a",
    overlay1= "#7f849c",
    text    = "#cdd6f4",
    subtext = "#a6adc8",
    blue    = "#89b4fa",
    green   = "#a6e3a1",
    red     = "#f38ba8",
    yellow  = "#f9e2af",
    teal    = "#94e2d5",
    mauve   = "#cba6f7",
    peach   = "#fab387",
)

# ─────────────────────────────────────────────────────────────────────────────
#  Logica di rinomina (pura — nessuna dipendenza GUI)
# ─────────────────────────────────────────────────────────────────────────────

def apply_rules(original_name: str, filepath: str, rules: dict,
                index: int, total: int) -> str:
    stem = Path(original_name).stem
    ext  = Path(original_name).suffix

    # 0 ── Riordina token ──────────────────────────────────────────────────
    if rules["token_delim"] and rules["token_template"]:
        parts = stem.split(rules["token_delim"])
        def _rt(m):
            i = int(m.group(1)) - 1
            return parts[i] if 0 <= i < len(parts) else m.group(0)
        try:
            stem = re.sub(r"\[\[(\d+)\]\]", _rt, rules["token_template"])
        except Exception:
            pass

    # 1 ── Trova / Sostituisci ─────────────────────────────────────────────
    if rules["find"]:
        try:
            if rules["use_regex"]:
                flags = 0 if rules["case_sensitive"] else re.IGNORECASE
                stem = re.sub(rules["find"], rules["replace"], stem, flags=flags)
            else:
                if rules["case_sensitive"]:
                    stem = stem.replace(rules["find"], rules["replace"])
                else:
                    stem = re.sub(re.escape(rules["find"]), rules["replace"],
                                  stem, flags=re.IGNORECASE)
        except re.error:
            pass

    # 2 ── Rimuovi caratteri ───────────────────────────────────────────────
    for ch in rules["remove_chars"]:
        stem = stem.replace(ch, "")

    # 3 ── Tronca ──────────────────────────────────────────────────────────
    if rules["truncate"] > 0:
        stem = stem[:rules["truncate"]]

    # 4 ── Case ────────────────────────────────────────────────────────────
    match rules["case_mode"]:
        case "lowercase":  stem = stem.lower()
        case "uppercase":  stem = stem.upper()
        case "titlecase":  stem = stem.title()
        case "camelcase":
            p = re.split(r"[\s_\-]+", stem)
            stem = p[0].lower() + "".join(x.title() for x in p[1:])
        case "snakecase":
            stem = re.sub(r"[\s\-]+", "_", stem).lower()
        case "kebabcase":
            stem = re.sub(r"[\s_]+", "-", stem).lower()

    # 5 ── Prefisso / Suffisso con token data ──────────────────────────────
    def expand(s: str) -> str:
        mt    = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
        pad   = len(str(total))
        toks  = {
            "[[MTIME_DATE]]":  mt.strftime("%Y%m%d"),
            "[[MTIME_YEAR]]":  mt.strftime("%Y"),
            "[[MTIME_MONTH]]": mt.strftime("%m"),
            "[[MTIME_DAY]]":   mt.strftime("%d"),
            "[[MTIME_TIME]]":  mt.strftime("%H%M%S"),
            "[[INDEX]]":       str(index + 1).zfill(pad),
            "[[INDEX0]]":      str(index).zfill(pad),
        }
        for k, v in toks.items():
            s = s.replace(k, v)
        return s

    stem = expand(rules["prefix"]) + stem + expand(rules["suffix"])

    # 6 ── Numerazione ─────────────────────────────────────────────────────
    if rules["numbering"]:
        num = str(rules["num_start"] + index).zfill(rules["num_pad"])
        sep = rules["num_sep"]
        if rules["num_pos"] == "prefix":
            stem = num + sep + stem
        else:
            stem = stem + sep + num

    # 7 ── Nuova estensione ────────────────────────────────────────────────
    if rules["new_ext"]:
        ne = rules["new_ext"]
        ext = ne if ne.startswith(".") else "." + ne

    # 8 ── Normalizza spazi ────────────────────────────────────────────────
    if rules["normalize_spaces"]:
        stem = re.sub(r"\s+", " ", stem).strip()

    return stem + ext


# ─────────────────────────────────────────────────────────────────────────────
#  Widget helpers
# ─────────────────────────────────────────────────────────────────────────────

def label(parent, text, size=13, weight="normal", color=None, **kw):
    return ctk.CTkLabel(parent, text=text, font=("monospace", size, weight),
                        text_color=color or C["text"], **kw)

def entry(parent, var, width=None, **kw):
    return ctk.CTkEntry(parent, textvariable=var,
                        fg_color=C["surface0"], border_color=C["surface1"],
                        text_color=C["text"],                        width=width or 400, **kw)

def check(parent, text, var, **kw):
    return ctk.CTkCheckBox(parent, text=text, variable=var,
                           text_color=C["subtext"],
                           fg_color=C["blue"], hover_color=C["mauve"],
                           font=("monospace", 12), **kw)

def btn(parent, text, cmd, fg=None, hover=None, width=130, **kw):
    return ctk.CTkButton(parent, text=text, command=cmd, width=width,
                         fg_color=fg or C["surface1"],
                         hover_color=hover or C["surface0"],
                         text_color=C["text"],
                         font=("monospace", 12), **kw)

def accent_btn(parent, text, cmd, **kw):
    return ctk.CTkButton(parent, text=text, command=cmd,
                         fg_color=C["blue"], hover_color=C["mauve"],
                         text_color=C["base"],
                         font=("monospace", 13, "bold"), **kw)

def section_frame(parent, title):
    """LabelFrame con titolo colorato."""
    outer = ctk.CTkFrame(parent, fg_color=C["mantle"],
                         corner_radius=8, border_width=1,
                         border_color=C["surface1"])
    outer.pack(fill="x", padx=6, pady=4)
    label(outer, f"  {title}", size=12, weight="bold",
          color=C["blue"]).pack(anchor="w", padx=6, pady=(6,2))
    inner = ctk.CTkFrame(outer, fg_color="transparent")
    inner.pack(fill="x", padx=8, pady=(0,8))
    inner.columnconfigure(1, weight=1)
    return inner


# ─────────────────────────────────────────────────────────────────────────────
#  Treeview nativa (customtkinter non ha Treeview)
# ─────────────────────────────────────────────────────────────────────────────

import tkinter.ttk as ttk

def _setup_treeview_style():
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("BR.Treeview",
                background=C["surface0"], foreground=C["text"],
                fieldbackground=C["surface0"], rowheight=24,
                font=("monospace", 10))
    s.configure("BR.Treeview.Heading",
                background=C["mantle"], foreground=C["blue"],
                font=("monospace", 10, "bold"), relief="flat")
    s.map("BR.Treeview",
          background=[("selected", C["surface1"])],
          foreground=[("selected", C["text"])])
    s.configure("BR.Vertical.TScrollbar",
                background=C["surface1"], troughcolor=C["mantle"],
                arrowcolor=C["overlay1"])


# ─────────────────────────────────────────────────────────────────────────────
#  App principale
# ─────────────────────────────────────────────────────────────────────────────

class BulkRenamerApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Bulk File Renamer")
        self.geometry("1200x740")
        self.minsize(960, 600)
        self.configure(fg_color=C["base"])
        _setup_treeview_style()

        self._files: list[str] = []
        self._undo_stack: list[list[tuple[str, str]]] = []
        self._tree_paths: dict[str, str] = {}           # iid -> full original path
        self._detail_visible = False

        self._build_ui()

    # ── Layout ────────────────────────────────────────────────────────────

    def _build_ui(self):
        # toolbar
        self._build_toolbar()

        # corpo - PanedWindow per sidebar ridimensionabile
        body = tk.PanedWindow(self, orient=tk.HORIZONTAL,
                              bg=C["base"], sashrelief=tk.FLAT,
                              sashwidth=6, sashpad=0,
                              sashcursor="sb_h_double_arrow")
        body.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        # colonna sinistra: pannello regole scrollabile
        left_wrap = ctk.CTkFrame(body, fg_color=C["mantle"],
                                 corner_radius=8, border_width=1,
                                 border_color=C["surface1"])

        self._rules_scroll = ctk.CTkScrollableFrame(
            left_wrap, fg_color="transparent", width=720)
        self._rules_scroll.pack(fill="both", expand=True)

        # colonna destra: preview
        right = ctk.CTkFrame(body, fg_color="transparent")

        body.add(left_wrap, minsize=350, width=760)
        body.add(right, minsize=250, width=400)

        self._build_rules_panel(self._rules_scroll)
        self._build_preview_panel(right)

    # ── Toolbar ───────────────────────────────────────────────────────────

    def _build_toolbar(self):
        tb = ctk.CTkFrame(self, fg_color=C["mantle"],
                          corner_radius=0, border_width=0, height=48)
        tb.pack(fill="x", side="top")
        tb.pack_propagate(False)

        pad = dict(padx=3, pady=8)
        btn(tb, "📂 Cartella",  self._open_folder, width=120).pack(side="left", **pad)
        btn(tb, "📄 File",      self._add_files,   width=90).pack(side="left", **pad)
        btn(tb, "🗑 Svuota",    self._clear_files,  width=90).pack(side="left", **pad)

        ctk.CTkFrame(tb, width=2, fg_color=C["surface1"]).pack(
            side="left", fill="y", padx=6, pady=6)

        btn(tb, "▶ Anteprima",  self._preview,  width=120).pack(side="left", **pad)
        accent_btn(tb, "✅ Rinomina!", self._rename, width=140).pack(side="left", **pad)
        btn(tb, "↩ Annulla",    self._undo,     width=110).pack(side="left", **pad)

        self._status_var = tk.StringVar(value="Nessun file caricato.")
        ctk.CTkLabel(tb, textvariable=self._status_var,
                     font=("monospace", 12),
                     text_color=C["blue"]).pack(side="right", padx=12)

    # ── Pannello regole ───────────────────────────────────────────────────

    def _build_rules_panel(self, parent):

        def row_lbl(frame, text, r, c=0):
            label(frame, text, size=12, color=C["subtext"]).grid(
                row=r, column=c, sticky="w", pady=2)

        def row_entry(frame, var, r, c=1, w=None):
            e = entry(frame, var, width=w)
            e.grid(row=r, column=c, sticky="ew", padx=(6, 0), pady=2)
            return e

        # ── 0. Riordina token ─────────────────────────────────────────────
        f = section_frame(parent, "🔀 Riordina token")
        row_lbl(f, "Delimitatore:", 0)
        self._token_delim_var = tk.StringVar(value=" - ")
        row_entry(f, self._token_delim_var, 0, w=80)
        row_lbl(f, "Template:", 1)
        self._token_tmpl_var = tk.StringVar()
        row_entry(f, self._token_tmpl_var, 1)
        label(f, "es: [[2]] - [[1]]  o  [[3]] - [[1]] - [[2]]",
              size=10, color=C["overlay1"]).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 2))
        self._token_preview_lbl = ctk.CTkLabel(
            f, text="", font=("monospace", 10),
            text_color=C["teal"],            wraplength=700, justify="left")
        self._token_preview_lbl.grid(row=3, column=0, columnspan=2, sticky="w")

        def _upd_token(*_):
            delim = self._token_delim_var.get()
            if not self._files or not delim:
                self._token_preview_lbl.configure(text="")
                return
            stem = Path(os.path.basename(self._files[0])).stem
            parts = stem.split(delim)
            t = "  ".join(f"[[{i+1}]]={p}" for i, p in enumerate(parts))
            self._token_preview_lbl.configure(text=f"Token: {t}")
            self._preview()

        self._token_delim_var.trace_add("write", _upd_token)
        self._token_tmpl_var.trace_add("write", _upd_token)

        # ── 1. Trova / Sostituisci ────────────────────────────────────────
        f = section_frame(parent, "🔍 Trova / Sostituisci")
        row_lbl(f, "Trova:", 0);     self._find_var = tk.StringVar();    row_entry(f, self._find_var, 0)
        row_lbl(f, "Sostituisci:", 1); self._replace_var = tk.StringVar(); row_entry(f, self._replace_var, 1)
        self._regex_var    = tk.BooleanVar()
        self._casesens_var = tk.BooleanVar()
        check(f, "Usa Regex",          self._regex_var).grid(   row=2, column=0, columnspan=2, sticky="w", pady=2)
        check(f, "Distingui maiusc.",  self._casesens_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=2)

        # ── 2. Rimuovi caratteri ──────────────────────────────────────────
        f = section_frame(parent, "✂ Rimuovi caratteri")
        row_lbl(f, "Caratteri:", 0)
        self._remove_var = tk.StringVar()
        row_entry(f, self._remove_var, 0)
        label(f, "es: .,;_# (ognuno rimosso singolarmente)",
              size=10, color=C["overlay1"]).grid(
            row=1, column=0, columnspan=2, sticky="w")

        # ── 3. Tronca ─────────────────────────────────────────────────────
        f = section_frame(parent, "✂ Tronca stem")
        row_lbl(f, "Max caratteri (0=off):", 0)
        self._trunc_var = tk.IntVar(value=0)
        ctk.CTkEntry(f, textvariable=self._trunc_var, width=60,
                     fg_color=C["surface0"], border_color=C["surface1"],
                     text_color=C["text"]).grid(row=0, column=1, sticky="w", padx=(6,0))

        # ── 4. Case ───────────────────────────────────────────────────────
        f = section_frame(parent, "🔠 Conversione case")
        self._case_var = tk.StringVar(value="none")
        cases = [("Nessuna","none"),("lowercase","lowercase"),
                 ("UPPERCASE","uppercase"),("Title Case","titlecase"),
                 ("camelCase","camelcase"),("snake_case","snakecase"),
                 ("kebab-case","kebabcase")]
        for i, (lbl_txt, val) in enumerate(cases):
            rb = ctk.CTkRadioButton(f, text=lbl_txt, variable=self._case_var, value=val,
                                    font=("monospace", 12), text_color=C["subtext"],
                                    fg_color=C["blue"], hover_color=C["mauve"])
            rb.grid(row=i // 2, column=i % 2, sticky="w", pady=1, padx=(0, 8))

        # ── 5. Prefisso / Suffisso ────────────────────────────────────────
        f = section_frame(parent, "➕ Prefisso / Suffisso")
        row_lbl(f, "Prefisso:", 0); self._prefix_var = tk.StringVar(); row_entry(f, self._prefix_var, 0)
        row_lbl(f, "Suffisso:", 1); self._suffix_var = tk.StringVar(); row_entry(f, self._suffix_var, 1)
        tokens = "[[MTIME_DATE]]  [[MTIME_YEAR]]\n[[MTIME_MONTH]]  [[MTIME_DAY]]  [[MTIME_TIME]]  [[INDEX]]"
        label(f, "Token:", size=10, color=C["overlay1"]).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))
        ctk.CTkLabel(f, text=tokens, font=("monospace", 10),
                     text_color=C["teal"], justify="left").grid(
            row=3, column=0, columnspan=2, sticky="w")

        # ── 6. Numerazione ────────────────────────────────────────────────
        f = section_frame(parent, "🔢 Numerazione sequenziale")
        self._num_var = tk.BooleanVar()
        check(f, "Abilita", self._num_var).grid(row=0, column=0, columnspan=2, sticky="w")

        row_lbl(f, "Posizione:", 1)
        self._numpos_var = tk.StringVar(value="suffix")
        ctk.CTkOptionMenu(f, variable=self._numpos_var, values=["suffix", "prefix"],
                          width=100, fg_color=C["surface0"],
                          button_color=C["surface1"],
                          button_hover_color=C["blue"],
                          text_color=C["text"],
                          font=("monospace", 12)).grid(
            row=1, column=1, sticky="w", padx=(6, 0), pady=2)

        row_lbl(f, "Separatore:", 2)
        self._numsep_var = tk.StringVar(value="_")
        ctk.CTkEntry(f, textvariable=self._numsep_var, width=50,
                     fg_color=C["surface0"], border_color=C["surface1"],
                     text_color=C["text"]).grid(row=2, column=1, sticky="w", padx=(6,0))

        row_lbl(f, "Inizia da:", 3)
        self._numstart_var = tk.IntVar(value=1)
        ctk.CTkEntry(f, textvariable=self._numstart_var, width=60,
                     fg_color=C["surface0"], border_color=C["surface1"],
                     text_color=C["text"]).grid(row=3, column=1, sticky="w", padx=(6,0))

        row_lbl(f, "Padding (cifre):", 4)
        self._numpad_var = tk.IntVar(value=3)
        ctk.CTkEntry(f, textvariable=self._numpad_var, width=60,
                     fg_color=C["surface0"], border_color=C["surface1"],
                     text_color=C["text"]).grid(row=4, column=1, sticky="w", padx=(6,0))

        # ── 7. Estensione ─────────────────────────────────────────────────
        f = section_frame(parent, "🔧 Cambia estensione")
        row_lbl(f, "Nuova estensione:", 0)
        self._ext_var = tk.StringVar()
        ctk.CTkEntry(f, textvariable=self._ext_var, width=90,
                     fg_color=C["surface0"], border_color=C["surface1"],
                     text_color=C["text"]).grid(row=0, column=1, sticky="w", padx=(6,0))
        label(f, "vuoto = mantieni originale", size=10,
              color=C["overlay1"]).grid(row=1, column=0, columnspan=2, sticky="w")

        # ── 8. Opzioni extra ──────────────────────────────────────────────
        f = section_frame(parent, "⚙ Opzioni")
        self._normspaces_var = tk.BooleanVar(value=True)
        check(f, "Normalizza spazi multipli", self._normspaces_var).grid(
            row=0, column=0, columnspan=2, sticky="w")

        # ── live preview su ogni cambio ───────────────────────────────────
        string_vars = [self._find_var, self._replace_var, self._prefix_var,
                       self._suffix_var, self._ext_var, self._remove_var,
                       self._numsep_var]
        bool_int_vars = [self._regex_var, self._casesens_var, self._num_var,
                         self._normspaces_var, self._numpos_var,
                         self._trunc_var, self._numstart_var, self._numpad_var,
                         self._case_var]
        for v in string_vars + bool_int_vars:
            v.trace_add("write", lambda *_: self._preview())

        # ── 9. Preset ─────────────────────────────────────────────────────
        f = section_frame(parent, "💾 Preset")
        btn_row = ctk.CTkFrame(f, fg_color="transparent")
        btn_row.grid(row=0, column=0, columnspan=2, sticky="w", pady=4)
        btn(btn_row, "💾 Salva preset",  self._save_preset, width=140).pack(side="left", padx=(0, 4))
        btn(btn_row, "📂 Carica preset", self._load_preset, width=140).pack(side="left")

    # ── Pannello preview (Treeview nativo) ────────────────────────────────

    def _build_preview_panel(self, parent):
        # header
        hdr = ctk.CTkFrame(parent, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 4))
        label(hdr, "FILE  /  ANTEPRIMA RINOMINA",
              size=13, weight="bold", color=C["blue"]).pack(side="left")
        self._conflict_label = ctk.CTkLabel(hdr, text="",
                                            font=("monospace", 12),
                                            text_color=C["red"])
        self._conflict_label.pack(side="right", padx=6)

        # treeview wrapper
        self._tree_frame = tree_frame = ctk.CTkFrame(parent, fg_color=C["mantle"],
                                  corner_radius=8, border_width=1,
                                  border_color=C["surface1"])
        tree_frame.pack(fill="both", expand=True)

        cols = ("orig", "nuovo", "stato")
        self._tree = ttk.Treeview(tree_frame, columns=cols,
                                  show="headings", selectmode="extended",
                                  style="BR.Treeview")
        self._tree.heading("orig",  text="Nome originale")
        self._tree.heading("nuovo", text="Nuovo nome")
        self._tree.heading("stato", text="Stato")
        self._tree.column("orig",  width=400, minwidth=160)
        self._tree.column("nuovo", width=400, minwidth=160)
        self._tree.column("stato", width=90,  minwidth=60, anchor="center")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self._tree.yview,
                            style="BR.Vertical.TScrollbar")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal",
                            command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set,
                             xscrollcommand=hsb.set)

        self._tree.tag_configure("col_orig",   foreground=C["text"])
        self._tree.tag_configure("col_nuovo",  foreground=C["yellow"])
        self._tree.tag_configure("changed",    foreground=C["green"])
        self._tree.tag_configure("unchanged",  foreground=C["overlay1"])
        self._tree.tag_configure("conflict",   foreground=C["red"])

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self._tree.pack(fill="both", expand=True)

        # pannello dettaglio (nascosto, compare alla selezione di una riga)
        self._detail_frame = ctk.CTkFrame(
            parent, fg_color=C["surface0"],
            corner_radius=6, border_width=1, border_color=C["surface1"])
        self._detail_frame.pack_forget()

        detail_inner = ctk.CTkFrame(self._detail_frame, fg_color="transparent")
        detail_inner.pack(fill="x", padx=10, pady=8)

        label(detail_inner, "📂 Percorso originale:", size=11, weight="bold",
              color=C["blue"]).pack(anchor="w")
        self._detail_orig = ctk.CTkLabel(
            detail_inner, text="", font=("monospace", 10),
            text_color=C["text"], wraplength=500, justify="left",
            anchor="w")
        self._detail_orig.pack(anchor="w", pady=(2, 8))

        label(detail_inner, "🔄 Nuovo percorso:", size=11, weight="bold",
              color=C["green"]).pack(anchor="w")
        self._detail_new = ctk.CTkLabel(
            detail_inner, text="", font=("monospace", 10),
            text_color=C["text"], wraplength=500, justify="left",
            anchor="w")
        self._detail_new.pack(anchor="w", pady=(2, 0))

        # bind selezione
        self._tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # pulsanti sotto
        btn_row = ctk.CTkFrame(parent, fg_color="transparent")
        btn_row.pack(fill="x", pady=(6, 0))
        btn(btn_row, "🗑 Rimuovi selezionati",
            self._remove_selected, width=180).pack(side="left", padx=2)
        btn(btn_row, "🔃 Ordina per nome",
            self._sort_by_name, width=160).pack(side="left", padx=2)

    # ── Raccolta regole ───────────────────────────────────────────────────

    def collect_rules(self) -> dict:
        def _int(v, default=0):
            try:
                return int(v.get())
            except (ValueError, tk.TclError):
                return default

        return {
            "token_delim":     self._token_delim_var.get(),
            "token_template":  self._token_tmpl_var.get(),
            "find":            self._find_var.get(),
            "replace":         self._replace_var.get(),
            "use_regex":       self._regex_var.get(),
            "case_sensitive":  self._casesens_var.get(),
            "remove_chars":    self._remove_var.get(),
            "truncate":        _int(self._trunc_var),
            "case_mode":       self._case_var.get(),
            "prefix":          self._prefix_var.get(),
            "suffix":          self._suffix_var.get(),
            "numbering":       self._num_var.get(),
            "num_pos":         self._numpos_var.get(),
            "num_sep":         self._numsep_var.get(),
            "num_start":       _int(self._numstart_var, 1),
            "num_pad":         _int(self._numpad_var, 3),
            "new_ext":         self._ext_var.get(),
            "normalize_spaces": self._normspaces_var.get(),
        }

    # ── Apply preset (load rules into UI) ─────────────────────────────────

    def _apply_preset(self, rules: dict):
        self._token_delim_var.set(rules.get("token_delim", ""))
        self._token_tmpl_var.set(rules.get("token_template", ""))
        self._find_var.set(rules.get("find", ""))
        self._replace_var.set(rules.get("replace", ""))
        self._regex_var.set(rules.get("use_regex", False))
        self._casesens_var.set(rules.get("case_sensitive", True))
        self._remove_var.set(rules.get("remove_chars", ""))
        self._trunc_var.set(rules.get("truncate", 0))
        self._case_var.set(rules.get("case_mode", "none"))
        self._prefix_var.set(rules.get("prefix", ""))
        self._suffix_var.set(rules.get("suffix", ""))
        self._num_var.set(rules.get("numbering", False))
        self._numpos_var.set(rules.get("num_pos", "suffix"))
        self._numsep_var.set(rules.get("num_sep", "_"))
        self._numstart_var.set(rules.get("num_start", 1))
        self._numpad_var.set(rules.get("num_pad", 3))
        self._ext_var.set(rules.get("new_ext", ""))
        self._normspaces_var.set(rules.get("normalize_spaces", True))
        self._preview()

    def _save_preset(self):
        name = simpledialog.askstring("Salva Preset", "Nome del preset:")
        if not name:
            return
        rules = self.collect_rules()
        preset = {"name": name, "rules": rules}
        path = filedialog.asksaveasfilename(
            title="Salva preset",
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            initialfile=f"{name}.json")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(preset, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Preset", f"Preset '{name}' salvato!")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile salvare: {e}")

    def _load_preset(self):
        path = filedialog.askopenfilename(
            title="Carica preset",
            filetypes=[("JSON", "*.json")],
            initialdir=os.path.expanduser("~"))
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                preset = json.load(f)
            rules = preset.get("rules", {})
            self._apply_preset(rules)
            name = preset.get("name", os.path.basename(path))
            messagebox.showinfo("Preset", f"Preset '{name}' caricato!")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare: {e}")

    # ── File management ───────────────────────────────────────────────────

    def _open_folder(self):
        folder = filedialog.askdirectory(title="Seleziona cartella")
        if not folder:
            return
        self._files = sorted(
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f))
        )
        self._preview()
        self._status_var.set(f"{len(self._files)} file da: {folder}")

    def _add_files(self):
        files = filedialog.askopenfilenames(title="Aggiungi file")
        if not files:
            return
        existing = set(self._files)
        self._files.extend(f for f in files if f not in existing)
        self._preview()
        self._status_var.set(f"{len(self._files)} file totali.")

    def _clear_files(self):
        self._files.clear()
        self._tree.delete(*self._tree.get_children())
        self._status_var.set("Lista svuotata.")

    def _remove_selected(self):
        sel = self._tree.selection()
        if not sel:
            return
        idxs = sorted((self._tree.index(s) for s in sel), reverse=True)
        for i in idxs:
            del self._files[i]
        self._preview()

    def _sort_by_name(self):
        self._files.sort(key=lambda p: os.path.basename(p).lower())
        self._preview()

    # ── Preview ───────────────────────────────────────────────────────────

    def _preview(self):
        self._tree.delete(*self._tree.get_children())
        self._tree_paths.clear()
        self._hide_detail()
        if not self._files:
            return

        rules     = self.collect_rules()
        total     = len(self._files)
        new_names = []

        for i, fp in enumerate(self._files):
            try:
                nuovo = apply_rules(os.path.basename(fp), fp, rules, i, total)
            except Exception as e:
                nuovo = f"[ERRORE: {e}]"
            new_names.append(nuovo)

        seen: dict[str, int] = {}
        for n in new_names:
            seen[n] = seen.get(n, 0) + 1

        conflicts = 0
        changed   = 0
        for fp, nuovo in zip(self._files, new_names):
            orig = os.path.basename(fp)
            is_conflict = seen[nuovo] > 1
            is_changed  = orig != nuovo

            if is_conflict:
                tag, stato = "conflict", "⚠ duplicato"
                conflicts += 1
            elif is_changed:
                tag, stato = "changed", "✓"
                changed += 1
            else:
                tag, stato = "unchanged", "—"

            iid = self._tree.insert("", "end",
                                    values=(orig, nuovo, stato),
                                    tags=(("col_orig",), ("col_nuovo",), (tag,)))
            self._tree_paths[iid] = fp

        if conflicts:
            self._conflict_label.configure(
                text=f"⚠ {conflicts} conflitti — rinomina bloccata")
        else:
            self._conflict_label.configure(text="")

        self._status_var.set(
            f"{total} file · {changed} da rinominare · {conflicts} conflitti")

    # ── Dettaglio selezione treeview ─────────────────────────────────────

    def _on_tree_select(self, event=None):
        sel = self._tree.selection()
        if not sel or len(sel) > 1:
            self._hide_detail()
            return

        iid = sel[0]
        fp = self._tree_paths.get(iid)
        if not fp:
            self._hide_detail()
            return

        values = self._tree.item(iid, "values")
        orig_name = values[0] if values else ""
        nuovo_name = values[1] if len(values) > 1 else ""

        # nuovo percorso completo
        new_fp = os.path.join(os.path.dirname(fp), nuovo_name) if nuovo_name else fp

        self._detail_orig.configure(text=fp)
        self._detail_new.configure(text=new_fp)

        if not self._detail_visible:
            self._detail_frame.pack(
                fill="x", after=self._tree_frame, pady=(6, 0))
            self._detail_visible = True

    def _hide_detail(self):
        if self._detail_visible:
            self._detail_frame.pack_forget()
            self._detail_visible = False

    # ── Rinomina ──────────────────────────────────────────────────────────

    def _rename(self):
        if not self._files:
            messagebox.showwarning("Bulk Renamer", "Nessun file nella lista.")
            return

        rules = self.collect_rules()
        total = len(self._files)
        pairs = [
            (fp, apply_rules(os.path.basename(fp), fp, rules, i, total))
            for i, fp in enumerate(self._files)
        ]

        new_names = [n for _, n in pairs]
        if len(set(new_names)) < len(new_names):
            messagebox.showerror("Conflitti",
                "Nomi duplicati nel risultato.\nRisolvi i conflitti prima di procedere.")
            return

        to_change = [(fp, n) for fp, n in pairs if os.path.basename(fp) != n]
        if not to_change:
            messagebox.showinfo("Bulk Renamer", "Nessun file da rinominare.")
            return

        if not messagebox.askyesno("Conferma",
                f"Rinominare {len(to_change)} file?\nOperazione reversibile con Annulla."):
            return

        done, errors = [], []
        for fp, new_name in to_change:
            new_fp = os.path.join(os.path.dirname(fp), new_name)
            try:
                os.rename(fp, new_fp)
                done.append((fp, new_fp))
                self._files[self._files.index(fp)] = new_fp
            except Exception as e:
                errors.append(f"{os.path.basename(fp)}: {e}")

        if done:
            self._undo_stack.append(done)

        self._preview()

        msg = f"✅ Rinominati: {len(done)} file."
        if errors:
            msg += f"\n\n⚠ Errori ({len(errors)}):\n" + "\n".join(errors[:10])
        messagebox.showinfo("Completato", msg)

    # ── Undo ─────────────────────────────────────────────────────────────

    def _undo(self):
        if not self._undo_stack:
            messagebox.showinfo("Annulla", "Nessuna operazione da annullare.")
            return

        last = self._undo_stack.pop()
        errors, restored = [], 0
        for old_fp, new_fp in reversed(last):
            try:
                os.rename(new_fp, old_fp)
                if new_fp in self._files:
                    self._files[self._files.index(new_fp)] = old_fp
                restored += 1
            except Exception as e:
                errors.append(f"{os.path.basename(new_fp)}: {e}")

        self._preview()
        msg = f"↩ Ripristinati: {restored} file."
        if errors:
            msg += f"\n\n⚠ Errori:\n" + "\n".join(errors[:10])
        messagebox.showinfo("Annulla", msg)


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = BulkRenamerApp()
    app.mainloop()
