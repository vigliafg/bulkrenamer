# Bulk File Renamer PRO

**Clone di ReNamer (den4b.com) in Python + PyQt6 con 17 regole di rinominazione componibili.**

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt-6-green.svg)
![Tema](https://img.shields.io/badge/Tema-Catppuccin%20Mocha-mauve.svg)

---

## Cos'è

Bulk File Renamer PRO è un'applicazione GUI per rinominare file in massa. Permette di comporre uno **stack di regole** (fino a 17 tipi diversi) e vedere in tempo reale l'anteprima del risultato, con colori che evidenziano modifiche e conflitti.

L'interfaccia è ispirata a [ReNamer](https://den4b.com) con tema scuro **Catppuccin Mocha**.

---

## Installazione

### Requisiti

- Python **3.10 o superiore**
- pip

### Dipendenze

L'unica dipendenza esterna è **PyQt6** (≥ 6.5). Tutto il resto è Python standard library.

| Pacchetto | Versione minima | Uso |
|-----------|----------------|-----|
| [PyQt6](https://pypi.org/project/PyQt6/) | ≥ 6.5 | GUI completa (finestre, widget, tabelle, splitter, menù) |

### Setup

```bash
# 1. Clona il repository
git clone <url-repo>
cd bulkrenamer

# 2. Crea un virtual environment (consigliato)
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# 3. Installa le dipendenze
pip install -r requirements.txt
```

### Avvio

```bash
python3 main.py
```

---

## Le 17 Regole

Ogni regola è un modulo indipendente che puoi aggiungere, rimuovere, riordinare, abilitare/disabilitare nello stack.

| # | Regola | Descrizione |
|---|--------|-------------|
| 1 | 📝 **Insert** | Inserisce testo prima, dopo, in una posizione specifica, o dopo/prima di un delimitatore. Supporta meta-tag `[[MTIME_DATE]]`, `[[INDEX]]`, ecc. |
| 2 | ✂️ **Delete** | Elimina un intervallo di caratteri (da posizione, delimitatore, o conteggio). |
| 3 | 🗑 **Remove** | Rimuove tutte le occorrenze di un testo (o solo la prima/ultima), con supporto case-sensitive e whole-word. Testi multipli con `*|*`. |
| 4 | 🔄 **Replace** | Trova e sostituisci testo con supporto regex, wildcard (`*` e `?`), case-sensitive e whole-word. |
| 5 | 🔀 **Rearrange** | Riordina i token del nome file usando delimitatori o posizioni esatte. Template con `$1`, `$2`, ecc. |
| 6 | 🔧 **Extension** | Cambia l'estensione del file. Può anche appendere e rimuovere duplicati consecutivi. |
| 7 | ✂️ **Strip** | Rimuove caratteri specifici (o set predefiniti: cifre, simboli, lettere, parentesi) da inizio, fine, o ovunque. Modalità invertita disponibile. |
| 8 | 🔠 **Case** | Converte: lowercase, UPPERCASE, Title Case, Inverti, Prima lettera maiuscola, Sentence case. Supporta frammenti forzati. |
| 9 | 🔢 **Serialize** | Numerazione sequenziale: decimale, romana, lettere inglesi (a-z, ba-bz...), note musicali. Padding, step, e reset personalizzabili. |
| 10 | 🎲 **Randomize** | Aggiunge una stringa casuale come prefisso/suffisso o sostituisce il nome. Lunghezza e set di caratteri configurabili. |
| 11 | 📏 **Padding** | Aggiunge/toglie padding agli zero nei numeri nel nome file. Supporta anche text padding (caratteri a sinistra o destra). |
| 12 | 🧹 **Clean Up** | Pulisce il nome: rimuove contenuto tra parentesi (tonde, quadre, graffe), normalizza spazi, divide camelCase, rimuove emoji e segni diacritici. |
| 13 | 🌍 **Translit** | Traslitterazione da alfabeti non-latini: Tedesco, Francese, Italiano, Spagnolo, Portoghese, Russo, Greco, Giapponese (Romaji) + mappe personalizzate. Bidirezionale. |
| 14 | 📅 **Reformat Date** | Rileva date nel nome file con regex e le riformatta (es. `2025-06-01` → `01062025`). |
| 15 | 🔣 **Regex** | Sostituzione con espressioni regolari arbitrarie. Per utenti avanzati. |
| 16 | 📋 **User Input** | Sostituisce i nomi file con una lista predefinita fornita dall'utente. |
| 17 | 🗺 **Mapping** | Rinomina basata su una mappa chiave-valore (vecchio nome → nuovo nome). |

---

## Meta-tag Disponibili

Alcune regole supportano meta-tag che vengono espansi dinamicamente:

| Tag | Descrizione |
|-----|-------------|
| `[[MTIME_DATE]]` | Data di modifica (`YYYYMMDD`) |
| `[[MTIME_YEAR]]` | Anno di modifica |
| `[[MTIME_MONTH]]` | Mese di modifica (`01`-`12`) |
| `[[MTIME_DAY]]` | Giorno di modifica (`01`-`31`) |
| `[[MTIME_TIME]]` | Ora di modifica (`HHMMSS`) |
| `[[INDEX]]` | Indice progressivo 1-based con padding automatico |
| `[[INDEX0]]` | Indice progressivo 0-based con padding automatico |

---

## Guida Rapida

### Flusso tipico

1. **Carica i file** — clicca `📂 Cartella` (carica tutti i file di una cartella) o `📄 File` (seleziona file specifici).
2. **Aggiungi regole** — dal menu `Regole` scegli le regole che ti servono. Appariranno nel pannello di sinistra come card impilabili.
3. **Configura ogni regola** — ogni card ha i suoi parametri. Puoi trascinare le regole per riordinarle (?), abilitarle/disabilitarle con la checkbox.
4. **Controlla l'anteprima** — il pannello di destra mostra: nome originale, nuovo nome, e stato (✓ modificato, ⚠ duplicato, — invariato).
5. **Seleziona i file** — spunta le checkbox nella colonna ☑ per ogni file che vuoi rinominare. Clicca l'intestazione ☑ per selezionare/deselezionare tutti.
6. **Rinomina!** — clicca `✅ Rinomina (N)` per applicare le modifiche ai file selezionati.

### Annulla

Dopo una rinomina, puoi annullare l'operazione con `↩ Annulla`. Lo stack di undo è illimitato.

### Preset

Puoi salvare la configurazione corrente delle regole in un file `.json` (`File → Salva preset`) e ricaricarla in seguito (`File → Carica preset`). Comodo per operazioni ripetitive!

### Factory Reset

`Strumenti → Factory Reset` riporta tutte le regole ai valori predefiniti.

---

## Struttura del Progetto

```
bulkrenamer/
├── main.py                  # Entry point dell'applicazione
├── renamer/
│   ├── app.py               # MainWindow: menù, toolbar, splitter, status bar
│   ├── engine.py            # Motore di rinomina (logica pura, zero GUI)
│   ├── theme.py             # Tema Catppuccin Mocha (palette colori + QSS)
│   ├── undo.py              # UndoManager (stack LIFO per annullare rinomine)
│   ├── preview.py           # PreviewTable: 4 colonne (☑ | Nome orig | Nuovo | Stato)
│   └── rules/
│       ├── __init__.py      # Registro ALL_RULES (17 regole)
│       ├── base.py          # Classe base RenameRule
│       ├── insert.py        # 📝 Insert
│       ├── delete.py        # ✂ Delete
│       ├── remove.py        # 🗑 Remove
│       ├── replace.py       # 🔄 Replace
│       ├── rearrange.py     # 🔀 Rearrange
│       ├── extension.py     # 🔧 Extension
│       ├── strip.py         # ✂ Strip
│       ├── case.py          # 🔠 Case
│       ├── serialize.py     # 🔢 Serialize
│       ├── randomize.py     # 🎲 Randomize
│       ├── padding.py       # 📏 Padding
│       ├── cleanup.py       # 🧹 Clean Up
│       ├── translit.py      # 🌍 Translit
│       ├── reformat_date.py # 📅 Reformat Date
│       ├── regex_rule.py    # 🔣 Regex
│       ├── user_input.py    # 📋 User Input
│       └── mapping.py       # 🗺 Mapping
```

---

## Licenza

Questo progetto è open source. Sentiti libero di usarlo, modificarlo e distribuirlo.

---

## Crediti

- **ReNamer** di [den4b.com](https://den4b.com) — ispirazione originale
- **Catppuccin Mocha** — palette del tema scuro
- **PyQt6** — framework GUI
