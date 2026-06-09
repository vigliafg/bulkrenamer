#!/usr/bin/env python3
"""
Bulk File Renamer PRO — GUI customtkinter
Funzionalità: trova/sostituisci (testo e regex), riordina token,
prefisso/suffisso con token data/EXIF, numerazione sequenziale,
cambio estensione, case conversion, undo illimitato, preview live,
menu Preferenze (colori e font personalizzabili), menu Aiuto (guida interattiva).

Dipendenze:
    pip install customtkinter
"""

import os
import re
import datetime
import json
import copy
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, colorchooser
from pathlib import Path

import customtkinter as ctk

# ── Config path ──────────────────────────────────────────────────────────────
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".bulk_renamer_pro.json")

# ── palette di fabbrica (Catppuccin Mocha) ───────────────────────────────────
FACTORY_C = dict(
    base     = "#1e1e2e",
    mantle   = "#181825",
    surface0 = "#313244",
    surface1 = "#45475a",
    overlay1 = "#7f849c",
    text     = "#cdd6f4",
    subtext  = "#a6adc8",
    blue     = "#89b4fa",
    green    = "#a6e3a1",
    red      = "#f38ba8",
    yellow   = "#f9e2af",
    teal     = "#94e2d5",
    mauve    = "#cba6f7",
    peach    = "#fab387",
)

FACTORY_FONTS = dict(
    label       = 13,
    label_small = 12,
    label_tiny  = 10,
    label_detail= 11,
    button      = 12,
    button_accent=13,
    tree        = 10,
    tree_heading= 10,
    radio       = 12,
    check       = 12,
    option      = 12,
    entry       = 13,
    toolbar     = 12,
)

# copia mutabile caricata da config o factory
C    = copy.deepcopy(FACTORY_C)
FONTS= copy.deepcopy(FACTORY_FONTS)

# ── Carica / Salva configurazione ────────────────────────────────────────────
def _load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        if "colors" in cfg:
            for k, v in cfg["colors"].items():
                if k in C:
                    C[k] = v
        if "fonts" in cfg:
            for k, v in cfg["fonts"].items():
                if k in FONTS:
                    FONTS[k] = int(v)
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        pass

def _save_config():
    try:
        cfg = {"colors": dict(C), "fonts": dict(FONTS)}
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

_load_config()

# ── Tema ─────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ─────────────────────────────────────────────────────────────────────────────
#  Logica di rinomina (pura — nessuna dipendenza GUI)
# ─────────────────────────────────────────────────────────────────────────────

def apply_rules(original_name: str, filepath: str, rules: dict,
                index: int, total: int) -> str:
    stem = Path(original_name).stem
    ext  = Path(original_name).suffix

    if rules["token_delim"] and rules["token_template"]:
        parts = stem.split(rules["token_delim"])
        def _rt(m):
            i = int(m.group(1)) - 1
            return parts[i] if 0 <= i < len(parts) else m.group(0)
        try:
            stem = re.sub(r"\[\[(\d+)\]\]", _rt, rules["token_template"])
        except Exception:
            pass

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

    for ch in rules["remove_chars"]:
        stem = stem.replace(ch, "")

    if rules["truncate"] > 0:
        stem = stem[:rules["truncate"]]

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

    if rules["numbering"]:
        num = str(rules["num_start"] + index).zfill(rules["num_pad"])
        sep = rules["num_sep"]
        if rules["num_pos"] == "prefix":
            stem = num + sep + stem
        else:
            stem = stem + sep + num

    if rules["new_ext"]:
        ne = rules["new_ext"]
        ext = ne if ne.startswith(".") else "." + ne

    if rules["normalize_spaces"]:
        stem = re.sub(r"\s+", " ", stem).strip()

    return stem + ext


# ─────────────────────────────────────────────────────────────────────────────
#  Widget helpers (colori e font da dizionari globali mutabili C / FONTS)
# ─────────────────────────────────────────────────────────────────────────────

def label(parent, text, size=None, weight="normal", color=None, **kw):
    return ctk.CTkLabel(parent, text=text,
                        font=("monospace", size or FONTS["label"], weight),
                        text_color=color or C["text"], **kw)

def entry(parent, var, width=None, **kw):
    return ctk.CTkEntry(parent, textvariable=var,
                        fg_color=C["surface0"], border_color=C["surface1"],
                        text_color=C["text"],
                        font=("monospace", FONTS["entry"]),
                        width=width or 400, **kw)

def check(parent, text, var, **kw):
    return ctk.CTkCheckBox(parent, text=text, variable=var,
                           text_color=C["subtext"],
                           fg_color=C["blue"], hover_color=C["mauve"],
                           font=("monospace", FONTS["check"]), **kw)

def btn(parent, text, cmd, fg=None, hover=None, width=130, **kw):
    return ctk.CTkButton(parent, text=text, command=cmd, width=width,
                         fg_color=fg or C["surface1"],
                         hover_color=hover or C["surface0"],
                         text_color=C["text"],
                         font=("monospace", FONTS["button"]), **kw)

def accent_btn(parent, text, cmd, **kw):
    return ctk.CTkButton(parent, text=text, command=cmd,
                         fg_color=C["blue"], hover_color=C["mauve"],
                         text_color=C["base"],
                         font=("monospace", FONTS["button_accent"], "bold"), **kw)

def section_frame(parent, title):
    outer = ctk.CTkFrame(parent, fg_color=C["mantle"],
                         corner_radius=8, border_width=1,
                         border_color=C["surface1"])
    outer.pack(fill="x", padx=6, pady=4)
    label(outer, f"  {title}", size=FONTS["label_small"], weight="bold",
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
                font=("monospace", FONTS["tree"]))
    s.configure("BR.Treeview.Heading",
                background=C["mantle"], foreground=C["blue"],
                font=("monospace", FONTS["tree_heading"], "bold"), relief="flat")
    s.map("BR.Treeview",
          background=[("selected", C["surface1"])],
          foreground=[("selected", C["text"])])
    s.configure("BR.Vertical.TScrollbar",
                background=C["surface1"], troughcolor=C["mantle"],
                arrowcolor=C["overlay1"])


# ─────────────────────────────────────────────────────────────────────────────
#  Handle PanedWindow sash (unico widget non-ctk, solo per resize)
# ─────────────────────────────────────────────────────────────────────────────

def _make_paned(parent, orient=tk.HORIZONTAL):
    return tk.PanedWindow(parent, orient=orient,
                          bg=C["base"], sashrelief=tk.FLAT,
                          sashwidth=6, sashpad=0,
                          sashcursor="sb_h_double_arrow")


# ─────────────────────────────────────────────────────────────────────────────
#  Guida ai tools (contenuti)
# ─────────────────────────────────────────────────────────────────────────────

TOOLS_HELP = [
    ("🔀 Riordina token", [
        "Riorganizza i \"token\" (parti) del nome file separati da un delimitatore.",
        "",
        "• Delimitatore: il carattere o la stringa che separa i token (es. ' - ', '_', ' ').",
        "• Template: schema di riordino. [[1]] = primo token, [[2]] = secondo, ecc.",
        "",
        "Esempio: file 'Report - 2025 - Q1.pdf' con delimitatore ' - ' e template '[[3]] - [[1]] - [[2]]'",
        "         diventa 'Q1 - Report - 2025.pdf'.",
        "",
        "I token non usati nel template vengono scartati.",
    ]),
    ("🔍 Trova / Sostituisci", [
        "Sostituisce testo nel nome del file (non nell'estensione).",
        "",
        "• Trova: testo o espressione regolare da cercare.",
        "• Sostituisci: testo con cui rimpiazzare.",
        "• Usa Regex: attiva le espressioni regolari (es. \\d+ per cifre).",
        "• Distingui maiusc.: rende la ricerca case-sensitive.",
        "",
        "Esempio (testo):     Trova='IMG'  Sostituisci='Foto'  → IMG_001.jpg → Foto_001.jpg",
        "Esempio (regex):     Trova='(\\d{4})-(\\d{2})-(\\d{2})'  Sostituisci='\\3-\\2-\\1'",
        "                     → 2025-06-01_report.txt → 01-06-2025_report.txt",
    ]),
    ("✂ Rimuovi caratteri", [
        "Elimina dal nome file ogni carattere elencato (uno per uno).",
        "",
        "• Inserisci i caratteri da rimuovere senza spazi (es. '.,;_#').",
        "• Ogni carattere viene rimosso singolarmente ovunque compaia.",
        "",
        "Esempio: Caratteri='-_#'  → 'My-File_#01.txt'  → 'MyFile01.txt'",
    ]),
    ("✂ Tronca stem", [
        "Tronca il nome del file (senza estensione) a N caratteri.",
        "",
        "• 0 = disabilitato.",
        "",
        "Esempio: Max=8  → 'molto_lungo_nome_file.txt' → 'molto_lu.txt'",
    ]),
    ("🔠 Conversione case", [
        "Cambia la capitalizzazione del nome file.",
        "",
        "• lowercase:  tutto minuscolo  →  mio file.txt",
        "• UPPERCASE:  tutto maiuscolo   →  MIO FILE.TXT",
        "• Title Case: Prime Lettere Maiuscole  →  Mio File.TXT",
        "• camelCase:  prima parola minuscola, resto maiuscole  →  mioFile.txt",
        "• snake_case: underscore tra parole, minuscolo  →  mio_file.txt",
        "• kebab-case: trattini tra parole, minuscolo  →  mio-file.txt",
    ]),
    ("➕ Prefisso / Suffisso", [
        "Aggiunge testo prima (prefisso) o dopo (suffisso) il nome file.",
        "",
        "Token disponibili:",
        "  [[MTIME_DATE]]  = data modifica (YYYYMMDD)",
        "  [[MTIME_YEAR]]  = anno modifica",
        "  [[MTIME_MONTH]] = mese modifica (01-12)",
        "  [[MTIME_DAY]]   = giorno modifica (01-31)",
        "  [[MTIME_TIME]]  = ora modifica (HHMMSS)",
        "  [[INDEX]]       = indice progressivo (1-based, padded)",
        "  [[INDEX0]]      = indice progressivo (0-based, padded)",
        "",
        "Esempio: Prefisso='[[MTIME_DATE]]_'  →  file.txt → 20250601_file.txt",
    ]),
    ("🔢 Numerazione sequenziale", [
        "Aggiunge un numero progressivo a ogni file.",
        "",
        "• Posizione: 'prefix' (prima) o 'suffix' (dopo il nome).",
        "• Separatore: carattere tra numero e nome (es. '_', '-').",
        "• Inizia da: primo numero della sequenza.",
        "• Padding: numero di cifre (es. 3 → 001, 002, ...).",
        "",
        "Esempio: Padding=3, Sep='_', Pos=suffix, Inizia=1",
        "  file_a.txt → file_a_001.txt",
        "  file_b.txt → file_b_002.txt",
    ]),
    ("🔧 Cambia estensione", [
        "Sostituisce l'estensione del file.",
        "",
        "• Lascia vuoto per mantenere l'estensione originale.",
        "• Il punto iniziale è opzionale (es. 'txt' e '.txt' sono equivalenti).",
        "",
        "Esempio: Nuova est.='md'  →  documento.txt → documento.md",
    ]),
    ("⚙ Opzioni", [
        "Opzioni aggiuntive di pulizia del nome file.",
        "",
        "• Normalizza spazi multipli: riduce sequenze di spazi a uno spazio singolo",
        "  e rimuove spazi iniziali e finali.",
        "",
        "Esempio: 'mio   file  .txt'  →  'mio file.txt'",
    ]),
    ("💾 Preset", [
        "Salva e carica configurazioni di regole per riutilizzarle.",
        "",
        "• Salva preset: esporta tutte le regole correnti in un file .json.",
        "• Carica preset: importa regole da un file .json precedentemente salvato.",
        "",
        "Utile per operazioni ripetitive con le stesse regole.",
    ]),
]


# ─────────────────────────────────────────────────────────────────────────────
#  App principale
# ─────────────────────────────────────────────────────────────────────────────

class BulkRenamerProApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Bulk File Renamer PRO")
        self.geometry("1200x740")
        self.minsize(960, 600)
        self.configure(fg_color=C["base"])
        _setup_treeview_style()

        self._files: list[str] = []
        self._undo_stack: list[list[tuple[str, str]]] = []
        self._tree_paths: dict[str, str] = {}
        self._detail_visible = False

        self._build_menubar()
        self._build_ui()

    # ── Menu bar ──────────────────────────────────────────────────────────

    def _build_menubar(self):
        menubar = tk.Menu(self, bg=C["mantle"], fg=C["text"],
                          activebackground=C["surface1"], activeforeground=C["text"],
                          font=("monospace", 11), relief=tk.FLAT, bd=0,
                          tearoff=0)
        self.configure(menu=menubar)

        # Menu Preferenze
        pref_menu = tk.Menu(menubar, tearoff=0,
                            bg=C["mantle"], fg=C["text"],
                            activebackground=C["surface1"],
                            activeforeground=C["blue"],
                            font=("monospace", 11))
        menubar.add_cascade(label="Preferenze", menu=pref_menu)
        pref_menu.add_command(label="🎨 Colori e Font …", command=self._open_preferences)
        pref_menu.add_separator()
        pref_menu.add_command(label="↺ Ripristina default", command=self._reset_preferences)

        # Menu Aiuto
        help_menu = tk.Menu(menubar, tearoff=0,
                            bg=C["mantle"], fg=C["text"],
                            activebackground=C["surface1"],
                            activeforeground=C["blue"],
                            font=("monospace", 11))
        menubar.add_cascade(label="Aiuto", menu=help_menu)
        help_menu.add_command(label="📖 Guida agli strumenti …", command=self._open_help)
        help_menu.add_separator()
        help_menu.add_command(label="ℹ Informazioni", command=self._show_about)

    # ── Layout ────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_toolbar()

        body = _make_paned(self)
        body.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        left_wrap = ctk.CTkFrame(body, fg_color=C["mantle"],
                                 corner_radius=8, border_width=1,
                                 border_color=C["surface1"])
        self._rules_scroll = ctk.CTkScrollableFrame(
            left_wrap, fg_color="transparent", width=720)
        self._rules_scroll.pack(fill="both", expand=True)

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
                     font=("monospace", FONTS["toolbar"]),
                     text_color=C["blue"]).pack(side="right", padx=12)

    # ── Pannello regole ───────────────────────────────────────────────────

    def _build_rules_panel(self, parent):

        def row_lbl(frame, text, r, c=0):
            label(frame, text, size=FONTS["label_small"], color=C["subtext"]).grid(
                row=r, column=c, sticky="w", pady=2)

        def row_entry(frame, var, r, c=1, w=None):
            e = entry(frame, var, width=w)
            e.grid(row=r, column=c, sticky="ew", padx=(6, 0), pady=2)
            return e

        # 0. Riordina token
        f = section_frame(parent, "🔀 Riordina token")
        row_lbl(f, "Delimitatore:", 0)
        self._token_delim_var = tk.StringVar(value=" - ")
        row_entry(f, self._token_delim_var, 0, w=80)
        row_lbl(f, "Template:", 1)
        self._token_tmpl_var = tk.StringVar()
        row_entry(f, self._token_tmpl_var, 1)
        label(f, "es: [[2]] - [[1]]  o  [[3]] - [[1]] - [[2]]",
              size=FONTS["label_tiny"], color=C["overlay1"]).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 2))
        self._token_preview_lbl = ctk.CTkLabel(
            f, text="", font=("monospace", FONTS["label_tiny"]),
            text_color=C["teal"], wraplength=700, justify="left")
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

        # 1. Trova / Sostituisci
        f = section_frame(parent, "🔍 Trova / Sostituisci")
        row_lbl(f, "Trova:", 0);     self._find_var = tk.StringVar();    row_entry(f, self._find_var, 0)
        row_lbl(f, "Sostituisci:", 1); self._replace_var = tk.StringVar(); row_entry(f, self._replace_var, 1)
        self._regex_var    = tk.BooleanVar()
        self._casesens_var = tk.BooleanVar()
        check(f, "Usa Regex",          self._regex_var).grid(   row=2, column=0, columnspan=2, sticky="w", pady=2)
        check(f, "Distingui maiusc.",  self._casesens_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=2)

        # 2. Rimuovi caratteri
        f = section_frame(parent, "✂ Rimuovi caratteri")
        row_lbl(f, "Caratteri:", 0)
        self._remove_var = tk.StringVar()
        row_entry(f, self._remove_var, 0)
        label(f, "es: .,;_# (ognuno rimosso singolarmente)",
              size=FONTS["label_tiny"], color=C["overlay1"]).grid(
            row=1, column=0, columnspan=2, sticky="w")

        # 3. Tronca
        f = section_frame(parent, "✂ Tronca stem")
        row_lbl(f, "Max caratteri (0=off):", 0)
        self._trunc_var = tk.IntVar(value=0)
        ctk.CTkEntry(f, textvariable=self._trunc_var, width=60,
                     fg_color=C["surface0"], border_color=C["surface1"],
                     text_color=C["text"],
                     font=("monospace", FONTS["entry"])).grid(
            row=0, column=1, sticky="w", padx=(6,0))

        # 4. Case
        f = section_frame(parent, "🔠 Conversione case")
        self._case_var = tk.StringVar(value="none")
        cases = [("Nessuna","none"),("lowercase","lowercase"),
                 ("UPPERCASE","uppercase"),("Title Case","titlecase"),
                 ("camelCase","camelcase"),("snake_case","snakecase"),
                 ("kebab-case","kebabcase")]
        for i, (lbl_txt, val) in enumerate(cases):
            rb = ctk.CTkRadioButton(f, text=lbl_txt, variable=self._case_var, value=val,
                                    font=("monospace", FONTS["radio"]), text_color=C["subtext"],
                                    fg_color=C["blue"], hover_color=C["mauve"])
            rb.grid(row=i // 2, column=i % 2, sticky="w", pady=1, padx=(0, 8))

        # 5. Prefisso / Suffisso
        f = section_frame(parent, "➕ Prefisso / Suffisso")
        row_lbl(f, "Prefisso:", 0); self._prefix_var = tk.StringVar(); row_entry(f, self._prefix_var, 0)
        row_lbl(f, "Suffisso:", 1); self._suffix_var = tk.StringVar(); row_entry(f, self._suffix_var, 1)
        tokens = "[[MTIME_DATE]]  [[MTIME_YEAR]]\n[[MTIME_MONTH]]  [[MTIME_DAY]]  [[MTIME_TIME]]  [[INDEX]]"
        label(f, "Token:", size=FONTS["label_tiny"], color=C["overlay1"]).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))
        ctk.CTkLabel(f, text=tokens, font=("monospace", FONTS["label_tiny"]),
                     text_color=C["teal"], justify="left").grid(
            row=3, column=0, columnspan=2, sticky="w")

        # 6. Numerazione
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
                          font=("monospace", FONTS["option"])).grid(
            row=1, column=1, sticky="w", padx=(6, 0), pady=2)

        row_lbl(f, "Separatore:", 2)
        self._numsep_var = tk.StringVar(value="_")
        ctk.CTkEntry(f, textvariable=self._numsep_var, width=50,
                     fg_color=C["surface0"], border_color=C["surface1"],
                     text_color=C["text"],
                     font=("monospace", FONTS["entry"])).grid(
            row=2, column=1, sticky="w", padx=(6,0))

        row_lbl(f, "Inizia da:", 3)
        self._numstart_var = tk.IntVar(value=1)
        ctk.CTkEntry(f, textvariable=self._numstart_var, width=60,
                     fg_color=C["surface0"], border_color=C["surface1"],
                     text_color=C["text"],
                     font=("monospace", FONTS["entry"])).grid(
            row=3, column=1, sticky="w", padx=(6,0))

        row_lbl(f, "Padding (cifre):", 4)
        self._numpad_var = tk.IntVar(value=3)
        ctk.CTkEntry(f, textvariable=self._numpad_var, width=60,
                     fg_color=C["surface0"], border_color=C["surface1"],
                     text_color=C["text"],
                     font=("monospace", FONTS["entry"])).grid(
            row=4, column=1, sticky="w", padx=(6,0))

        # 7. Estensione
        f = section_frame(parent, "🔧 Cambia estensione")
        row_lbl(f, "Nuova estensione:", 0)
        self._ext_var = tk.StringVar()
        ctk.CTkEntry(f, textvariable=self._ext_var, width=90,
                     fg_color=C["surface0"], border_color=C["surface1"],
                     text_color=C["text"],
                     font=("monospace", FONTS["entry"])).grid(
            row=0, column=1, sticky="w", padx=(6,0))
        label(f, "vuoto = mantieni originale", size=FONTS["label_tiny"],
              color=C["overlay1"]).grid(row=1, column=0, columnspan=2, sticky="w")

        # 8. Opzioni extra
        f = section_frame(parent, "⚙ Opzioni")
        self._normspaces_var = tk.BooleanVar(value=True)
        check(f, "Normalizza spazi multipli", self._normspaces_var).grid(
            row=0, column=0, columnspan=2, sticky="w")

        # live preview
        string_vars = [self._find_var, self._replace_var, self._prefix_var,
                       self._suffix_var, self._ext_var, self._remove_var,
                       self._numsep_var]
        bool_int_vars = [self._regex_var, self._casesens_var, self._num_var,
                         self._normspaces_var, self._numpos_var,
                         self._trunc_var, self._numstart_var, self._numpad_var,
                         self._case_var]
        for v in string_vars + bool_int_vars:
            v.trace_add("write", lambda *_: self._preview())

        # 9. Preset
        f = section_frame(parent, "💾 Preset")
        btn_row = ctk.CTkFrame(f, fg_color="transparent")
        btn_row.grid(row=0, column=0, columnspan=2, sticky="w", pady=4)
        btn(btn_row, "💾 Salva preset",  self._save_preset, width=140).pack(side="left", padx=(0, 4))
        btn(btn_row, "📂 Carica preset", self._load_preset, width=140).pack(side="left")

    # ── Pannello preview ──────────────────────────────────────────────────

    def _build_preview_panel(self, parent):
        hdr = ctk.CTkFrame(parent, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 4))
        label(hdr, "FILE  /  ANTEPRIMA RINOMINA",
              size=13, weight="bold", color=C["blue"]).pack(side="left")
        self._conflict_label = ctk.CTkLabel(hdr, text="",
                                            font=("monospace", FONTS["label_small"]),
                                            text_color=C["red"])
        self._conflict_label.pack(side="right", padx=6)

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
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self._tree.tag_configure("col_orig",   foreground=C["text"])
        self._tree.tag_configure("col_nuovo",  foreground=C["yellow"])
        self._tree.tag_configure("changed",    foreground=C["green"])
        self._tree.tag_configure("unchanged",  foreground=C["overlay1"])
        self._tree.tag_configure("conflict",   foreground=C["red"])

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self._tree.pack(fill="both", expand=True)

        # pannello dettaglio
        self._detail_frame = ctk.CTkFrame(
            parent, fg_color=C["surface0"],
            corner_radius=6, border_width=1, border_color=C["surface1"])
        self._detail_frame.pack_forget()

        detail_inner = ctk.CTkFrame(self._detail_frame, fg_color="transparent")
        detail_inner.pack(fill="x", padx=10, pady=8)

        label(detail_inner, "📂 Percorso originale:", size=FONTS["label_detail"],
              weight="bold", color=C["blue"]).pack(anchor="w")
        self._detail_orig = ctk.CTkLabel(
            detail_inner, text="", font=("monospace", FONTS["label_tiny"]),
            text_color=C["text"], wraplength=500, justify="left", anchor="w")
        self._detail_orig.pack(anchor="w", pady=(2, 8))

        label(detail_inner, "🔄 Nuovo percorso:", size=FONTS["label_detail"],
              weight="bold", color=C["green"]).pack(anchor="w")
        self._detail_new = ctk.CTkLabel(
            detail_inner, text="", font=("monospace", FONTS["label_tiny"]),
            text_color=C["text"], wraplength=500, justify="left", anchor="w")
        self._detail_new.pack(anchor="w", pady=(2, 0))

        self._tree.bind("<<TreeviewSelect>>", self._on_tree_select)

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
                                    tags=((("col_orig",), ("col_nuovo",), (tag,))))
            self._tree_paths[iid] = fp

        if conflicts:
            self._conflict_label.configure(
                text=f"⚠ {conflicts} conflitti — rinomina bloccata")
        else:
            self._conflict_label.configure(text="")
        self._status_var.set(
            f"{total} file · {changed} da rinominare · {conflicts} conflitti")

    # ── Dettaglio selezione ───────────────────────────────────────────────

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
        new_fp = os.path.join(os.path.dirname(fp), nuovo_name) if nuovo_name else fp
        self._detail_orig.configure(text=fp)
        self._detail_new.configure(text=new_fp)
        if not self._detail_visible:
            self._detail_frame.pack(fill="x", after=self._tree_frame, pady=(6, 0))
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

    # ══════════════════════════════════════════════════════════════════════
    #  FINESTRA PREFERENZE (CTkToplevel)
    # ══════════════════════════════════════════════════════════════════════

    def _open_preferences(self):
        w = ctk.CTkToplevel(self)
        w.title("Preferenze — Colori e Font")
        w.geometry("680x680")
        w.minsize(580, 500)
        w.configure(fg_color=C["base"])
        w.grab_set()
        w.after(100, w.lift)

        # copie locali per edit senza side-effect immediato
        local_colors = copy.deepcopy(C)
        local_fonts  = copy.deepcopy(FONTS)
        local_vars: dict[str, tk.StringVar] = {}
        font_vars: dict[str, tk.StringVar] = {}

        # ── Pannello anteprima live ─────────────────────────────────────
        preview_outer = ctk.CTkFrame(w, fg_color=C["surface0"],
                                     corner_radius=8, border_width=1,
                                     border_color=C["surface1"])
        preview_outer.pack(fill="x", padx=10, pady=(10, 6))

        pv_inner = ctk.CTkFrame(preview_outer, fg_color="transparent")
        pv_inner.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(pv_inner, text="👁 Anteprima tema:",
                     font=("monospace", 11, "bold"),
                     text_color=C["blue"]).pack(anchor="w", pady=(0, 6))

        pv_row = ctk.CTkFrame(pv_inner, fg_color="transparent")
        pv_row.pack(fill="x")

        pv_label_demo = ctk.CTkLabel(
            pv_row, text="Testo Label",
            font=("monospace", local_fonts["label"], "normal"),
            text_color=local_colors["text"])
        pv_label_demo.pack(side="left", padx=(0, 12))

        pv_btn_demo = ctk.CTkButton(
            pv_row, text="Bottone Demo",
            fg_color=local_colors["blue"],
            hover_color=local_colors["mauve"],
            text_color=local_colors["base"],
            font=("monospace", local_fonts["button"], "bold"),
            state="disabled")
        pv_btn_demo.pack(side="left", padx=(0, 12))

        pv_small = ctk.CTkLabel(
            pv_row, text="Note / Esempi",
            font=("monospace", local_fonts["label_tiny"], "normal"),
            text_color=local_colors["overlay1"])
        pv_small.pack(side="left")

        def _update_preview():
            """Aggiorna l'anteprima coi valori correnti di local_colors / local_fonts."""
            try:
                def _fs(key, fallback):
                    v = font_vars.get(key)
                    return int(v.get()) if v else fallback
                fs_label = _fs("label", local_fonts.get("label", 13))
                fs_btn   = _fs("button", local_fonts.get("button", 12))
                fs_tiny  = _fs("label_tiny", local_fonts.get("label_tiny", 10))
                pv_label_demo.configure(
                    font=("monospace", fs_label, "normal"),
                    text_color=local_colors.get("text", C["text"]))
                pv_btn_demo.configure(
                    fg_color=local_colors.get("blue", C["blue"]),
                    hover_color=local_colors.get("mauve", C["mauve"]),
                    text_color=local_colors.get("base", C["base"]),
                    font=("monospace", fs_btn, "bold"))
                pv_small.configure(
                    font=("monospace", fs_tiny, "normal"),
                    text_color=local_colors.get("overlay1", C["overlay1"]))
                preview_outer.configure(fg_color=local_colors.get("surface0", C["surface0"]))
            except Exception:
                pass

        # notebook (tabview) per colori / font
        tab = ctk.CTkTabview(w, fg_color=C["mantle"],
                             segmented_button_fg_color=C["surface1"],
                             segmented_button_selected_color=C["blue"],
                             segmented_button_unselected_color=C["surface1"],
                             segmented_button_unselected_hover_color=C["surface0"],
                             text_color=C["text"],
                             border_color=C["surface1"], border_width=1)
        tab.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        tab.add("🎨 Colori")
        tab.add("🔤 Font")
        # attiva tab colori per primo
        tab.set("🎨 Colori")

        # ── Tab Colori ────────────────────────────────────────────────
        color_frame = ctk.CTkScrollableFrame(tab.tab("🎨 Colori"),
                                             fg_color="transparent")
        color_frame.pack(fill="both", expand=True, padx=4, pady=4)

        for key in local_colors:
            row = ctk.CTkFrame(color_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{key}:", width=90, anchor="w",
                         font=("monospace", 12),
                         text_color=C["subtext"]).pack(side="left", padx=(6, 4))

            # quadratino anteprima colore
            preview = ctk.CTkFrame(row, width=28, height=28,
                                   fg_color=local_colors[key],
                                   corner_radius=4,
                                   border_width=1, border_color=C["surface1"])
            preview.pack(side="left", padx=(0, 6))

            var = tk.StringVar(value=local_colors[key])
            local_vars[key] = var
            e = ctk.CTkEntry(row, textvariable=var, width=110,
                             fg_color=C["surface0"], border_color=C["surface1"],
                             text_color=C["text"],
                             font=("monospace", 12))
            e.pack(side="left")

            # pulsante color picker
            def _make_picker(_pv=preview, _v=var, _k=key):
                def _pick():
                    _, hexc = colorchooser.askcolor(
                        color=_v.get(), title=f"Scegli colore: {_k}",
                        parent=w)
                    if hexc:
                        _v.set(hexc)
                        local_colors[_k] = hexc
                        _pv.configure(fg_color=hexc)
                        _update_preview()
                return _pick
            ctk.CTkButton(row, text="🎨", width=32, height=28,
                          fg_color=C["surface1"], hover_color=C["blue"],
                          text_color=C["text"],
                          font=("monospace", 12),
                          command=_make_picker()).pack(side="left", padx=(4, 0))

            # aggiorna anteprima live mentre scrivi
            def _make_updater(_pv=preview, _v=var, _k=key):
                def _upd(*_):
                    val = _v.get().strip()
                    if val.startswith("#") and len(val) in (4, 7):
                        try:
                            _pv.configure(fg_color=val)
                            local_colors[_k] = val
                            _update_preview()
                        except Exception:
                            pass
                return _upd
            var.trace_add("write", _make_updater())

        # ── Tab Font ──────────────────────────────────────────────────
        font_frame = ctk.CTkScrollableFrame(tab.tab("🔤 Font"),
                                            fg_color="transparent")
        font_frame.pack(fill="both", expand=True, padx=4, pady=4)

        font_descriptions = {
            "label":          "Label principali",
            "label_small":    "Label sezioni / regole",
            "label_tiny":     "Label note / esempi",
            "label_detail":   "Label pannello dettaglio",
            "button":         "Bottoni standard",
            "button_accent":  "Bottone accent (Rinomina!)",
            "tree":           "Treeview (nomi file)",
            "tree_heading":   "Treeview (intestazioni)",
            "radio":          "Radio button",
            "check":          "Checkbox",
            "option":         "Option menu",
            "entry":          "Campi input",
            "toolbar":        "Status bar",
        }

        for key, desc in font_descriptions.items():
            row = ctk.CTkFrame(font_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=desc, width=140, anchor="w",
                         font=("monospace", 12),
                         text_color=C["subtext"]).pack(side="left", padx=(6, 4))
            ctk.CTkLabel(row, text=f"({key})", width=100, anchor="w",
                         font=("monospace", 10),
                         text_color=C["overlay1"]).pack(side="left", padx=(0, 6))
            var = tk.StringVar(value=str(local_fonts.get(key, 12)))
            font_vars[key] = var
            ctk.CTkEntry(row, textvariable=var, width=55,
                         fg_color=C["surface0"], border_color=C["surface1"],
                         text_color=C["text"],
                         font=("monospace", 12)).pack(side="left")
            # aggiorna anteprima quando cambia un font
            var.trace_add("write", lambda *_, v=var: _update_preview())

        # ── Pulsanti in basso ──────────────────────────────────────────
        btn_bar = ctk.CTkFrame(w, fg_color="transparent")
        btn_bar.pack(fill="x", padx=10, pady=10)

        accent_btn(btn_bar, "✅ Applica",
                   lambda: self._apply_prefs(local_vars, font_vars, w),
                   width=130).pack(side="right", padx=(4, 0))
        btn(btn_bar, "↺ Factory Reset",
            lambda: self._factory_reset_prefs(local_vars, font_vars, local_colors, local_fonts, w),
            fg=C["red"], hover="#cc6a80", width=140).pack(side="right", padx=4)
        btn(btn_bar, "Annulla", w.destroy, width=90).pack(side="right", padx=(0, 8))

    def _apply_prefs(self, local_vars, font_vars, win):
        """Applica i valori dai campi e salva la configurazione."""
        changed = False
        for key, var in local_vars.items():
            val = var.get().strip()
            if val and val != C.get(key, ""):
                C[key] = val
                changed = True
        for key, var in font_vars.items():
            try:
                val = int(var.get())
                if val > 0 and val != FONTS.get(key, 0):
                    FONTS[key] = val
                    changed = True
            except ValueError:
                pass

        if changed:
            _save_config()
            # aggiorna ciò che possiamo aggiornare live
            self.configure(fg_color=C["base"])
            _setup_treeview_style()
            self._tree.tag_configure("col_orig",   foreground=C["text"])
            self._tree.tag_configure("col_nuovo",  foreground=C["yellow"])
            self._tree.tag_configure("changed",    foreground=C["green"])
            self._tree.tag_configure("unchanged",  foreground=C["overlay1"])
            self._tree.tag_configure("conflict",   foreground=C["red"])
            messagebox.showinfo("Preferenze",
                "Preferenze applicate e salvate.\n"
                "Alcune modifiche (es. pannello regole) richiedono il riavvio\n"
                "per avere effetto completo.",
                parent=win)
        win.destroy()

    def _factory_reset_prefs(self, local_vars, font_vars, local_colors, local_fonts, win):
        """Riporta i campi della finestra ai valori di fabbrica."""
        for key, var in local_vars.items():
            default = FACTORY_C.get(key, "")
            var.set(default)
            local_colors[key] = default
        for key, var in font_vars.items():
            default = str(FACTORY_FONTS.get(key, 12))
            var.set(default)
            local_fonts[key] = int(default)
        messagebox.showinfo("Factory Reset",
            "Valori riportati ai default di fabbrica.\n"
            "Clicca 'Applica' per salvare.",
            parent=win)

    def _reset_preferences(self):
        """Dal menu: ripristina tutto ai default e salva."""
        if not messagebox.askyesno("Ripristina default",
                "Ripristinare TUTTI i colori e font ai valori di fabbrica?\n"
                "La configurazione salvata verrà sovrascritta."):
            return
        C.clear();    C.update(FACTORY_C)
        FONTS.clear(); FONTS.update(FACTORY_FONTS)
        _save_config()
        self.configure(fg_color=C["base"])
        _setup_treeview_style()
        messagebox.showinfo("Ripristino",
            "Colori e font ripristinati ai default.\n"
            "Riavvia l'applicazione per applicare completamente le modifiche.")

    # ══════════════════════════════════════════════════════════════════════
    #  FINESTRA AIUTO (CTkToplevel)
    # ══════════════════════════════════════════════════════════════════════

    def _open_help(self):
        w = ctk.CTkToplevel(self)
        w.title("Guida agli strumenti")
        w.geometry("700x580")
        w.minsize(500, 400)
        w.configure(fg_color=C["base"])
        w.grab_set()
        w.after(100, w.lift)

        # header
        hdr = ctk.CTkFrame(w, fg_color="transparent")
        hdr.pack(fill="x", padx=12, pady=(12, 4))
        ctk.CTkLabel(hdr, text="📖 Guida agli strumenti",
                     font=("monospace", 16, "bold"),
                     text_color=C["blue"]).pack(side="left")
        ctk.CTkLabel(hdr, text="Seleziona uno strumento dalla lista",
                     font=("monospace", 11),
                     text_color=C["overlay1"]).pack(side="left", padx=12)

        body = _make_paned(w, orient=tk.HORIZONTAL)
        body.pack(fill="both", expand=True, padx=10, pady=(4, 10))

        # lista tools a sinistra
        list_frame = ctk.CTkFrame(body, fg_color=C["mantle"],
                                  corner_radius=8, border_width=1,
                                  border_color=C["surface1"])

        list_scroll = ctk.CTkScrollableFrame(list_frame, fg_color="transparent",
                                             width=280)
        list_scroll.pack(fill="both", expand=True, padx=4, pady=4)

        # pannello descrizione a destra
        desc_frame = ctk.CTkFrame(body, fg_color=C["mantle"],
                                  corner_radius=8, border_width=1,
                                  border_color=C["surface1"])

        body.add(list_frame, minsize=200, width=280)
        body.add(desc_frame, minsize=250, width=400)

        desc_title = ctk.CTkLabel(desc_frame, text="",
                                  font=("monospace", 14, "bold"),
                                  text_color=C["blue"], anchor="w")
        desc_title.pack(anchor="w", padx=14, pady=(12, 4))

        desc_sep = ctk.CTkFrame(desc_frame, height=1, fg_color=C["surface1"])
        desc_sep.pack(fill="x", padx=14, pady=(0, 8))

        desc_text = ctk.CTkLabel(desc_frame, text="",
                                 font=("monospace", 11),
                                 text_color=C["text"],
                                 justify="left", anchor="w")
        desc_text.pack(anchor="w", padx=14, pady=(0, 14), fill="x")

        # wraplength dinamico
        def _adj_wrap(event=None):
            ww = desc_frame.winfo_width()
            if ww > 50:
                desc_text.configure(wraplength=ww - 30)
        desc_frame.bind("<Configure>", _adj_wrap)
        desc_text.bind("<Configure>", lambda e: _adj_wrap())

        # bottoni per ogni tool
        tool_buttons: list[ctk.CTkButton] = []

        def _show_desc(idx: int):
            title, lines = TOOLS_HELP[idx]
            desc_title.configure(text=title)
            desc_text.configure(text="\n".join(lines))
            for i, b in enumerate(tool_buttons):
                if i == idx:
                    b.configure(fg_color=C["blue"], text_color=C["base"])
                else:
                    b.configure(fg_color=C["surface1"], text_color=C["text"])

        for i, (title, _) in enumerate(TOOLS_HELP):
            b = ctk.CTkButton(
                list_scroll, text=title, anchor="w",
                fg_color=C["surface1"] if i > 0 else C["blue"],
                hover_color=C["surface0"],
                text_color=C["text"] if i > 0 else C["base"],
                font=("monospace", 11),
                command=lambda idx=i: _show_desc(idx))
            b.pack(fill="x", pady=1)
            tool_buttons.append(b)

        # mostra primo tool
        _show_desc(0)

        # chiudi
        btn(w, "Chiudi", w.destroy, width=90).pack(pady=(0, 8))

    def _show_about(self):
        messagebox.showinfo("Bulk File Renamer PRO",
            "Bulk File Renamer PRO v2.0\n\n"
            "GUI per la rinominazione in massa di file.\n"
            "Tema: Catppuccin Mocha (personalizzabile)\n"
            "Basato su customtkinter + tkinter.\n\n"
            "Funzionalità principali:\n"
            "• Trova/Sostituisci con regex\n"
            "• Riordino token\n"
            "• Numerazione sequenziale\n"
            "• Prefisso/Suffisso con data/ora\n"
            "• Conversione case\n"
            "• Undo illimitato\n"
            "• Preset salvabili\n"
            "• Interfaccia completamente personalizzabile\n\n"
            "Dipendenze: pip install customtkinter")


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = BulkRenamerProApp()
    app.mainloop()
