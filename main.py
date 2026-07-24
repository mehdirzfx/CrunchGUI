#!/usr/bin/env python3
"""
Crunch GUI - Simple, compact, responsive frontend for the Crunch wordlist generator
Author: Mehdi Rezaei Far
Github : https://github.com/mehdirzfx
"""
import os
import json
import shutil
import subprocess
import threading
import queue
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PRESETS_FILE = os.path.join(APP_DIR, "crunch_gui_presets.json")
GITHUB_URL = "https://github.com/mehdirzfx"
APP_VERSION = "1.0.0"

CHARSET_LOWER = "abcdefghijklmnopqrstuvwxyz"
CHARSET_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CHARSET_DIGITS = "0123456789"
CHARSET_SYMBOLS = "!@#$%^&*()-_=+"
COMPRESSION_OPTIONS = ["none", "gzip", "bzip2", "lzma", "7z"]

PATTERN_LEGEND = "@ lower   , upper   % digit   ^ symbol   (else = literal)"

DEFAULT_PRESETS = {
    "PIN - 4 digits": {
        "mode": "charset", "pattern": "", "min_len": 4, "max_len": 4,
        "custom_charset": "", "use_lower": False, "use_upper": False, "use_digits": True, "use_symbols": False,
        "output": "pin_4digit.txt", "split_count": "", "dup_limit": "", "permute": False,
        "permute_words": "", "start": "", "end": "", "compression": "none",
    },
    "PIN - 6 digits": {
        "mode": "charset", "pattern": "", "min_len": 6, "max_len": 6,
        "custom_charset": "", "use_lower": False, "use_upper": False, "use_digits": True, "use_symbols": False,
        "output": "pin_6digit.txt", "split_count": "", "dup_limit": "", "permute": False,
        "permute_words": "", "start": "", "end": "", "compression": "none",
    },
    "Router/WiFi PIN - 8 digits": {
        "mode": "charset", "pattern": "", "min_len": 8, "max_len": 8,
        "custom_charset": "", "use_lower": False, "use_upper": False, "use_digits": True, "use_symbols": False,
        "output": "router_pin_8digit.txt", "split_count": "", "dup_limit": "", "permute": False,
        "permute_words": "", "start": "", "end": "", "compression": "none",
    },
    "Password - lowercase 6-8 chars": {
        "mode": "charset", "pattern": "", "min_len": 6, "max_len": 8,
        "custom_charset": "", "use_lower": True, "use_upper": False, "use_digits": False, "use_symbols": False,
        "output": "password_lower.txt", "split_count": "", "dup_limit": "", "permute": False,
        "permute_words": "", "start": "", "end": "", "compression": "none",
    },
    "Password - lowercase+digits 8-10 chars": {
        "mode": "charset", "pattern": "", "min_len": 8, "max_len": 10,
        "custom_charset": "", "use_lower": True, "use_upper": False, "use_digits": True, "use_symbols": False,
        "output": "password_alnum.txt", "split_count": "", "dup_limit": "", "permute": False,
        "permute_words": "", "start": "", "end": "", "compression": "none",
    },
    "Password - strong (upper+lower+digit+symbol) 8-12": {
        "mode": "charset", "pattern": "", "min_len": 8, "max_len": 12,
        "custom_charset": "", "use_lower": True, "use_upper": True, "use_digits": True, "use_symbols": True,
        "output": "password_strong.txt", "split_count": "", "dup_limit": "", "permute": False,
        "permute_words": "", "start": "", "end": "", "compression": "none",
    },
    "Username - user0000 to user9999": {
        "mode": "pattern", "pattern": "user%%%%", "min_len": 8, "max_len": 8,
        "custom_charset": "", "use_lower": False, "use_upper": False, "use_digits": True, "use_symbols": False,
        "output": "usernames_user.txt", "split_count": "", "dup_limit": "", "permute": False,
        "permute_words": "", "start": "", "end": "", "compression": "none",
    },
    "Username - admin + 3 digits": {
        "mode": "pattern", "pattern": "admin%%%", "min_len": 8, "max_len": 8,
        "custom_charset": "", "use_lower": False, "use_upper": False, "use_digits": True, "use_symbols": False,
        "output": "usernames_admin.txt", "split_count": "", "dup_limit": "", "permute": False,
        "permute_words": "", "start": "", "end": "", "compression": "none",
    },
    "Phone number - 10 digits": {
        "mode": "pattern", "pattern": "%%%%%%%%%%", "min_len": 10, "max_len": 10,
        "custom_charset": "", "use_lower": False, "use_upper": False, "use_digits": True, "use_symbols": False,
        "output": "phone_numbers.txt", "split_count": "", "dup_limit": "", "permute": False,
        "permute_words": "", "start": "", "end": "", "compression": "none",
    },
    "Date - DDMMYYYY": {
        "mode": "pattern", "pattern": "%%%%%%%%", "min_len": 8, "max_len": 8,
        "custom_charset": "", "use_lower": False, "use_upper": False, "use_digits": True, "use_symbols": False,
        "output": "dates.txt", "split_count": "", "dup_limit": "", "permute": False,
        "permute_words": "", "start": "", "end": "", "compression": "none",
    },
    "Date - YYYYMMDD": {
        "mode": "pattern", "pattern": "%%%%%%%%", "min_len": 8, "max_len": 8,
        "custom_charset": "", "use_lower": False, "use_upper": False, "use_digits": True, "use_symbols": False,
        "output": "dates_ymd.txt", "split_count": "", "dup_limit": "", "permute": False,
        "permute_words": "", "start": "", "end": "", "compression": "none",
    },
    "Date - MM-DD-YYYY": {
        "mode": "pattern", "pattern": "%%-%%-%%%%", "min_len": 10, "max_len": 10,
        "custom_charset": "", "use_lower": False, "use_upper": False, "use_digits": True, "use_symbols": False,
        "output": "dates_mdy.txt", "split_count": "", "dup_limit": "", "permute": False,
        "permute_words": "", "start": "", "end": "", "compression": "none",
    },
    "ZIP / postal code - 5 digits": {
        "mode": "charset", "pattern": "", "min_len": 5, "max_len": 5,
        "custom_charset": "", "use_lower": False, "use_upper": False, "use_digits": True, "use_symbols": False,
        "output": "zip_codes.txt", "split_count": "", "dup_limit": "", "permute": False,
        "permute_words": "", "start": "", "end": "", "compression": "none",
    },
    "Hex string - 8 chars": {
        "mode": "charset", "pattern": "", "min_len": 8, "max_len": 8,
        "custom_charset": "0123456789abcdef", "use_lower": False, "use_upper": False,
        "use_digits": False, "use_symbols": False,
        "output": "hex_8.txt", "split_count": "", "dup_limit": "", "permute": False,
        "permute_words": "", "start": "", "end": "", "compression": "none",
    },
    "MAC-like address (XX:XX:XX:XX:XX:XX)": {
        "mode": "pattern", "pattern": "%%:%%:%%:%%:%%:%%", "min_len": 17, "max_len": 17,
        "custom_charset": "0123456789abcdef", "use_lower": False, "use_upper": False,
        "use_digits": False, "use_symbols": False,
        "output": "mac_like.txt", "split_count": "", "dup_limit": "", "permute": False,
        "permute_words": "", "start": "", "end": "", "compression": "none",
    },
    "Password - mixed case + digits, 8 chars": {
        "mode": "charset", "pattern": "", "min_len": 8, "max_len": 8,
        "custom_charset": "", "use_lower": True, "use_upper": True, "use_digits": True, "use_symbols": False,
        "output": "password_mixed.txt", "split_count": "", "dup_limit": "", "permute": False,
        "permute_words": "", "start": "", "end": "", "compression": "none",
    },
    "Username - user_XX (2 digits)": {
        "mode": "pattern", "pattern": "user_%%", "min_len": 7, "max_len": 7,
        "custom_charset": "", "use_lower": False, "use_upper": False, "use_digits": True, "use_symbols": False,
        "output": "usernames_user_xx.txt", "split_count": "", "dup_limit": "", "permute": False,
        "permute_words": "", "start": "", "end": "", "compression": "none",
    },
}

THEMES = {
    "light": {
        "bg": "#f4f4f6", "fg": "#1e1e1e", "panel": "#ffffff",
        "entry_bg": "#ffffff", "entry_fg": "#1e1e1e",
        "accent": "#2563eb", "accent_fg": "#ffffff",
        "muted": "#666666", "border": "#d5d5d9",
        "log_bg": "#ffffff", "log_fg": "#1e1e1e",
        "select_bg": "#dbe6ff", "error": "#c0392b", "ok": "#1e7d34",
    },
    "dark": {
        "bg": "#1e1f26", "fg": "#e8e8ec", "panel": "#262832",
        "entry_bg": "#2f3140", "entry_fg": "#e8e8ec",
        "accent": "#5b8cff", "accent_fg": "#ffffff",
        "muted": "#9a9aa5", "border": "#3a3c48",
        "log_bg": "#15161c", "log_fg": "#d6d6dd",
        "select_bg": "#3a4a6b", "error": "#ff6b6b", "ok": "#4fd67a",
    },
}


def load_presets():
    presets = dict(DEFAULT_PRESETS)
    if os.path.exists(PRESETS_FILE):
        try:
            with open(PRESETS_FILE, "r", encoding="utf-8") as f:
                presets.update(json.load(f))
        except Exception:
            pass
    return presets


def save_user_presets(all_presets):
    user_only = {n: d for n, d in all_presets.items()
                 if n not in DEFAULT_PRESETS or DEFAULT_PRESETS[n] != d}
    try:
        with open(PRESETS_FILE, "w", encoding="utf-8") as f:
            json.dump(user_only, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showerror("Error saving presets", str(e))


def find_crunch_exe():
    for name in ("crunch.exe", "crunch"):
        p = os.path.join(APP_DIR, name)
        if os.path.exists(p):
            return p
    return shutil.which("crunch") or shutil.which("crunch.exe") or ""


class CrunchGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Crunch GUI • v" + APP_VERSION)
        self.geometry("680x600")
        self.minsize(560, 480)

        self.presets = load_presets()
        self.process = None
        self.log_queue = queue.Queue()
        self.theme_name = "light"
        self.tk_widgets_to_theme = []
        self._loading_preset = False

        self.crunch_path_var = tk.StringVar(value=find_crunch_exe())
        self.mode_var = tk.StringVar(value="charset")
        self.min_len_var = tk.IntVar(value=5)
        self.max_len_var = tk.IntVar(value=5)
        self.use_lower_var = tk.BooleanVar(value=True)
        self.use_upper_var = tk.BooleanVar(value=False)
        self.use_digits_var = tk.BooleanVar(value=False)
        self.use_symbols_var = tk.BooleanVar(value=False)
        self.custom_charset_var = tk.StringVar(value="")
        self.pattern_var = tk.StringVar(value="")
        self.output_var = tk.StringVar(value=os.path.join(APP_DIR, "wordlist.txt"))
        self.split_count_var = tk.StringVar(value="")
        self.dup_limit_var = tk.StringVar(value="")
        self.start_var = tk.StringVar(value="")
        self.end_var = tk.StringVar(value="")
        self.compression_var = tk.StringVar(value="none")
        self.permute_var = tk.BooleanVar(value=False)
        self.permute_words_var = tk.StringVar(value="")
        self.preset_var = tk.StringVar(value="")

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self._build_layout()
        self._center_window()
        self._apply_theme("light")
        self._validate_and_estimate()
        self.after(100, self._poll_log_queue)

        for var in (self.custom_charset_var, self.pattern_var, self.min_len_var, self.max_len_var,
                    self.output_var, self.crunch_path_var, self.permute_words_var):
            var.trace_add("write", lambda *_: self._validate_and_estimate())

    # ------------------------------------------------------------------
    # Overall window layout: top bar / notebook (expands) / fixed footer
    # ------------------------------------------------------------------
    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_layout(self):
        top = ttk.Frame(self, padding=(10, 8))
        top.pack(fill="x", side="top")
        ttk.Label(top, text="Crunch GUI", font=("Segoe UI", 12, "bold")).pack(side="left")
        self.theme_btn = ttk.Button(top, text="Dark mode", command=self._toggle_theme, width=11)
        self.theme_btn.pack(side="right")

        # Footer packed BEFORE the notebook so it reserves its space at the
        # bottom and stays fixed/visible while the notebook above scrolls/resizes.
        footer = ttk.Frame(self, padding=(10, 4, 10, 8))
        footer.pack(fill="x", side="bottom")
        self._build_footer(footer)

        ttk.Separator(self, orient="horizontal").pack(fill="x", side="bottom")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 6), side="top")

        self.tab_quick = ttk.Frame(self.notebook)
        self.tab_advanced = ttk.Frame(self.notebook)
        self.tab_about = ttk.Frame(self.notebook, padding=14)

        self.notebook.add(self.tab_quick, text="Quick Setup")
        self.notebook.add(self.tab_advanced, text="Advanced")
        self.notebook.add(self.tab_about, text="About")

        self._build_quick_tab()
        self._build_advanced_tab()
        self._build_about_tab()

    # ------------------------------------------------------------------
    # Reusable scrollable-frame helper (mouse-wheel enabled)
    # ------------------------------------------------------------------
    def _make_scrollable(self, parent):
        canvas = tk.Canvas(parent, highlightthickness=0, borderwidth=0)
        vscroll = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas, padding=12)

        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_inner_configure(_e=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(e):
            canvas.itemconfig(window_id, width=e.width)

        inner.bind("<Configure>", _on_inner_configure)
        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(yscrollcommand=vscroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        vscroll.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_wheel(_e=None):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_wheel(_e=None):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_wheel)
        canvas.bind("<Leave>", _unbind_wheel)

        self.tk_widgets_to_theme.append(("canvas", canvas))
        return inner

    # ------------------------------------------------------------------
    # Quick Setup tab (scrollable)
    # ------------------------------------------------------------------
    def _build_quick_tab(self):
        f = self._make_scrollable(self.tab_quick)

        preset_row = ttk.Frame(f)
        preset_row.pack(fill="x", pady=(0, 8))
        ttk.Label(preset_row, text="Preset:").pack(side="left")
        self.preset_combo = ttk.Combobox(preset_row, textvariable=self.preset_var,
                                          values=list(self.presets.keys()), state="readonly", width=28)
        self.preset_combo.pack(side="left", padx=6)
        self.preset_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_config_dict(
            self.presets[self.preset_var.get()]))
        ttk.Button(preset_row, text="Save", width=6, command=self._save_current_as_preset).pack(side="left", padx=2)
        ttk.Button(preset_row, text="Delete", width=7, command=self._delete_selected_preset).pack(side="left")

        ttk.Label(f, text="crunch.exe path:").pack(anchor="w")
        path_row = ttk.Frame(f)
        path_row.pack(fill="x", pady=(0, 10))
        ttk.Entry(path_row, textvariable=self.crunch_path_var).pack(side="left", fill="x", expand=True)
        ttk.Button(path_row, text="Browse", command=self._browse_crunch).pack(side="left", padx=6)

        mode_row = ttk.Frame(f)
        mode_row.pack(fill="x", pady=(0, 6))
        ttk.Radiobutton(mode_row, text="Simple (pick characters)", variable=self.mode_var,
                         value="charset", command=self._on_mode_change).pack(side="left")
        ttk.Radiobutton(mode_row, text="Pattern (fixed layout)", variable=self.mode_var,
                         value="pattern", command=self._on_mode_change).pack(side="left", padx=12)

        len_row = ttk.Frame(f)
        len_row.pack(fill="x", pady=(0, 8))
        ttk.Label(len_row, text="Length:").pack(side="left")
        ttk.Spinbox(len_row, from_=1, to=64, textvariable=self.min_len_var, width=5).pack(side="left", padx=(6, 3))
        ttk.Label(len_row, text="to").pack(side="left")
        ttk.Spinbox(len_row, from_=1, to=64, textvariable=self.max_len_var, width=5).pack(side="left", padx=3)

        self.charset_frame = ttk.LabelFrame(f, text="Characters to use", padding=10)
        cf = self.charset_frame
        ttk.Checkbutton(cf, text="a-z", variable=self.use_lower_var, command=self._validate_and_estimate).grid(
            row=0, column=0, sticky="w", padx=6, pady=3)
        ttk.Checkbutton(cf, text="A-Z", variable=self.use_upper_var, command=self._validate_and_estimate).grid(
            row=0, column=1, sticky="w", padx=6, pady=3)
        ttk.Checkbutton(cf, text="0-9", variable=self.use_digits_var, command=self._validate_and_estimate).grid(
            row=0, column=2, sticky="w", padx=6, pady=3)
        ttk.Checkbutton(cf, text="symbols", variable=self.use_symbols_var, command=self._validate_and_estimate).grid(
            row=0, column=3, sticky="w", padx=6, pady=3)
        ttk.Label(cf, text="extra chars:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(cf, textvariable=self.custom_charset_var, width=26).grid(
            row=1, column=1, columnspan=3, sticky="we", pady=(6, 0))

        self.pattern_frame = ttk.LabelFrame(f, text="Pattern", padding=10)
        pf = self.pattern_frame
        ttk.Entry(pf, textvariable=self.pattern_var, font=("Consolas", 10)).pack(fill="x")
        ttk.Label(pf, text=PATTERN_LEGEND, foreground="#777").pack(anchor="w", pady=(4, 0))
        qrow = ttk.Frame(pf)
        qrow.pack(anchor="w", pady=(4, 0))
        for label, token in [("@", "@"), (",", ","), ("%", "%"), ("^", "^")]:
            ttk.Button(qrow, text=label, width=3,
                       command=lambda t=token: self.pattern_var.set(self.pattern_var.get() + t)
                       ).pack(side="left", padx=2)

        self.charset_frame.pack(fill="x", pady=5)
        self.pattern_frame.pack(fill="x", pady=5)
        self._on_mode_change()

        ttk.Label(f, text="Save output as:").pack(anchor="w", pady=(8, 0))
        out_row = ttk.Frame(f)
        out_row.pack(fill="x")
        ttk.Entry(out_row, textvariable=self.output_var).pack(side="left", fill="x", expand=True)
        ttk.Button(out_row, text="Browse", command=self._browse_output).pack(side="left", padx=6)

    def _on_mode_change(self):
        if self.mode_var.get() == "charset":
            self.pattern_frame.pack_forget()
            self.charset_frame.pack(fill="x", pady=5)
        else:
            self.charset_frame.pack_forget()
            self.pattern_frame.pack(fill="x", pady=5)
        self._validate_and_estimate()

    def _build_effective_charset(self):
        chars = ""
        if self.use_lower_var.get():
            chars += CHARSET_LOWER
        if self.use_upper_var.get():
            chars += CHARSET_UPPER
        if self.use_digits_var.get():
            chars += CHARSET_DIGITS
        if self.use_symbols_var.get():
            chars += CHARSET_SYMBOLS
        chars += self.custom_charset_var.get()
        seen, result = set(), []
        for c in chars:
            if c not in seen:
                seen.add(c)
                result.append(c)
        return "".join(result)

    # ------------------------------------------------------------------
    # Advanced tab (scrollable, compact)
    # ------------------------------------------------------------------
    def _build_advanced_tab(self):
        f = self._make_scrollable(self.tab_advanced)

        grid = ttk.Frame(f)
        grid.pack(fill="x")
        rows = [
            ("Split every N lines (-c):", self.split_count_var, 14),
            ("Max duplicate chars, e.g. 2@ (-d):", self.dup_limit_var, 14),
            ("Start string (-s):", self.start_var, 18),
            ("End string (-e):", self.end_var, 18),
        ]
        for i, (label, var, width) in enumerate(rows):
            ttk.Label(grid, text=label).grid(row=i, column=0, sticky="w", pady=4)
            ttk.Entry(grid, textvariable=var, width=width).grid(row=i, column=1, sticky="w", padx=10)

        ttk.Label(grid, text="Compression (-z):").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Combobox(grid, textvariable=self.compression_var, values=COMPRESSION_OPTIONS,
                     state="readonly", width=10).grid(row=4, column=1, sticky="w", padx=10)

        perm = ttk.LabelFrame(f, text="Permutation mode (-p): rearrange given words, no charset", padding=10)
        perm.pack(fill="x", pady=12)
        ttk.Checkbutton(perm, text="Enable", variable=self.permute_var,
                        command=self._validate_and_estimate).pack(anchor="w")
        ttk.Label(perm, text="Words (space separated):").pack(anchor="w", pady=(4, 0))
        ttk.Entry(perm, textvariable=self.permute_words_var).pack(fill="x")

    def _browse_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialdir=APP_DIR,
                                             filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            self.output_var.set(path)

    def _browse_crunch(self):
        path = filedialog.askopenfilename(initialdir=APP_DIR,
                                           filetypes=[("Executable", "*.exe"), ("All files", "*.*")])
        if path:
            self.crunch_path_var.set(path)

    # ------------------------------------------------------------------
    # Preset save / delete
    # ------------------------------------------------------------------
    def _refresh_preset_combo(self):
        self.preset_combo["values"] = list(self.presets.keys())

    def _current_config_as_dict(self):
        return {
            "mode": self.mode_var.get(), "pattern": self.pattern_var.get(),
            "min_len": self.min_len_var.get(), "max_len": self.max_len_var.get(),
            "custom_charset": self.custom_charset_var.get(),
            "use_lower": self.use_lower_var.get(), "use_upper": self.use_upper_var.get(),
            "use_digits": self.use_digits_var.get(), "use_symbols": self.use_symbols_var.get(),
            "output": self.output_var.get(), "split_count": self.split_count_var.get(),
            "dup_limit": self.dup_limit_var.get(), "permute": self.permute_var.get(),
            "permute_words": self.permute_words_var.get(), "start": self.start_var.get(),
            "end": self.end_var.get(), "compression": self.compression_var.get(),
        }

    def _apply_config_dict(self, cfg):
        self._loading_preset = True
        self.mode_var.set(cfg.get("mode", "charset"))
        self.pattern_var.set(cfg.get("pattern", ""))
        self.min_len_var.set(cfg.get("min_len", 4))
        self.max_len_var.set(cfg.get("max_len", 8))
        self.custom_charset_var.set(cfg.get("custom_charset", ""))
        self.use_lower_var.set(cfg.get("use_lower", True))
        self.use_upper_var.set(cfg.get("use_upper", False))
        self.use_digits_var.set(cfg.get("use_digits", False))
        self.use_symbols_var.set(cfg.get("use_symbols", False))
        self.output_var.set(cfg.get("output", os.path.join(APP_DIR, "wordlist.txt")))
        self.split_count_var.set(cfg.get("split_count", ""))
        self.dup_limit_var.set(cfg.get("dup_limit", ""))
        self.permute_var.set(cfg.get("permute", False))
        self.permute_words_var.set(cfg.get("permute_words", ""))
        self.start_var.set(cfg.get("start", ""))
        self.end_var.set(cfg.get("end", ""))
        self.compression_var.set(cfg.get("compression", "none"))
        self._loading_preset = False
        self._on_mode_change()

    def _save_current_as_preset(self):
        top = tk.Toplevel(self)
        top.title("Save Preset")
        top.geometry("300x100")
        ttk.Label(top, text="Preset name:").pack(anchor="w", padx=10, pady=(10, 0))
        name_var = tk.StringVar()
        entry = ttk.Entry(top, textvariable=name_var)
        entry.pack(fill="x", padx=10, pady=5)
        entry.focus()

        def do_save():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Save Preset", "Enter a name.", parent=top)
                return
            self.presets[name] = self._current_config_as_dict()
            save_user_presets(self.presets)
            self._refresh_preset_combo()
            self.preset_var.set(name)
            top.destroy()

        ttk.Button(top, text="Save", command=do_save).pack(pady=5)

    def _delete_selected_preset(self):
        name = self.preset_var.get()
        if not name or name not in self.presets:
            messagebox.showinfo("Delete Preset", "Pick a preset from the dropdown first.")
            return
        if messagebox.askyesno("Delete Preset", f"Delete '{name}'?"):
            self.presets.pop(name, None)
            save_user_presets(self.presets)
            self._refresh_preset_combo()
            self.preset_var.set("")

    # ------------------------------------------------------------------
    # About tab
    # ------------------------------------------------------------------
    def _build_about_tab(self):
        f = self.tab_about
        ttk.Label(f, text="Crunch GUI", font=("Segoe UI", 15, "bold")).pack(anchor="w")
        ttk.Label(f, text=f"Version {APP_VERSION}", foreground="#777").pack(anchor="w", pady=(0, 10))
        ttk.Label(f, text="A simple, preset-driven interface for the Crunch wordlist generator.",
                  wraplength=520, justify="left").pack(anchor="w", pady=(0, 14))
        ttk.Label(f, text="Developer:").pack(anchor="w")
        ttk.Label(f, text="mehdirzfx", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 10))
        ttk.Label(f, text="GitHub:").pack(anchor="w")
        link = ttk.Label(f, text=GITHUB_URL, foreground="#2563eb", cursor="hand2")
        link.pack(anchor="w")
        link.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_URL))
        ttk.Button(f, text="Open GitHub profile", command=lambda: webbrowser.open(GITHUB_URL)).pack(
            anchor="w", pady=8)

    # ------------------------------------------------------------------
    # Footer: status line + run/stop + small scrollable log (always visible)
    # ------------------------------------------------------------------
    def _build_footer(self, footer):
        self.status_label = tk.Label(footer, text="", anchor="w", justify="left",
                                      font=("Segoe UI", 9, "bold"), bd=0)
        self.status_label.pack(fill="x", pady=(0, 4))
        self.tk_widgets_to_theme.append(("status", self.status_label))

        run_row = ttk.Frame(footer)
        run_row.pack(fill="x", pady=(0, 4))
        self.run_button = ttk.Button(run_row, text="▶ Run", command=self._run_crunch)
        self.run_button.pack(side="right")
        self.stop_button = ttk.Button(run_row, text="■ Stop", command=self._stop_crunch, state="disabled")
        self.stop_button.pack(side="right", padx=6)
        ttk.Label(run_row, text="Log:").pack(side="left")

        self.log_text = scrolledtext.ScrolledText(footer, font=("Consolas", 9), state="disabled",
                                                    relief="flat", borderwidth=0, height=6, wrap="none")
        self.log_text.pack(fill="x", expand=False)
        self.tk_widgets_to_theme.append(("text", self.log_text))

    # ------------------------------------------------------------------
    # Theming
    # ------------------------------------------------------------------
    def _toggle_theme(self):
        self._apply_theme("dark" if self.theme_name == "light" else "light")

    def _apply_theme(self, name):
        self.theme_name = name
        t = THEMES[name]
        s = self.style

        self.configure(bg=t["bg"])
        s.configure(".", background=t["bg"], foreground=t["fg"], fieldbackground=t["entry_bg"])
        s.configure("TFrame", background=t["bg"])
        s.configure("TLabel", background=t["bg"], foreground=t["fg"])
        s.configure("TLabelframe", background=t["bg"], foreground=t["fg"], bordercolor=t["border"])
        s.configure("TLabelframe.Label", background=t["bg"], foreground=t["fg"])
        s.configure("TCheckbutton", background=t["bg"], foreground=t["fg"])
        s.configure("TRadiobutton", background=t["bg"], foreground=t["fg"])
        s.configure("TNotebook", background=t["bg"], bordercolor=t["border"])
        s.configure("TNotebook.Tab", background=t["panel"], foreground=t["fg"], padding=(10, 5))
        s.map("TNotebook.Tab",
              background=[("selected", t["accent"])],
              foreground=[("selected", t["accent_fg"])])
        s.configure("TButton", background=t["panel"], foreground=t["fg"], bordercolor=t["border"])
        s.map("TButton", background=[("active", t["accent"])], foreground=[("active", t["accent_fg"])])
        s.configure("TEntry", fieldbackground=t["entry_bg"], foreground=t["entry_fg"],
                    bordercolor=t["border"])
        s.configure("TCombobox", fieldbackground=t["entry_bg"], foreground=t["entry_fg"],
                    background=t["panel"])
        s.configure("TSpinbox", fieldbackground=t["entry_bg"], foreground=t["entry_fg"])
        s.configure("TScrollbar", background=t["panel"], troughcolor=t["bg"], bordercolor=t["border"])

        for kind, widget in self.tk_widgets_to_theme:
            if kind == "text":
                widget.configure(bg=t["log_bg"], fg=t["log_fg"], insertbackground=t["fg"])
            elif kind == "status":
                widget.configure(bg=t["bg"])
            elif kind == "canvas":
                widget.configure(bg=t["bg"])

        self.theme_btn.configure(text="Dark mode" if name == "light" else "Light mode")
        self._validate_and_estimate()

    # ------------------------------------------------------------------
    # Validation + live inline status (no popups)
    # ------------------------------------------------------------------
    def _set_status(self, text, kind="ok"):
        t = THEMES[self.theme_name]
        color = {"ok": t["fg"], "error": t["error"], "good": t["ok"]}.get(kind, t["fg"])
        self.status_label.configure(text=text, fg=color)

    def _validate_and_estimate(self):
        if self._loading_preset:
            return
        if not hasattr(self, "status_label"):
            return
        try:
            min_len, max_len = self.min_len_var.get(), self.max_len_var.get()
        except Exception:
            self._set_status("Length must be a whole number.", "error")
            return

        if min_len < 1 or max_len < 1:
            self._set_status("Length must be at least 1.", "error")
            return
        if min_len > max_len:
            self._set_status("Min length cannot be greater than max length.", "error")
            return

        if self.mode_var.get() == "charset":
            charset = self._build_effective_charset()
            if not charset:
                self._set_status("Pick at least one character group (a-z, A-Z, 0-9, symbols) or add extra characters.", "error")
                return
            total = sum(len(charset) ** n for n in range(min_len, max_len + 1))
            avg_len = (min_len + max_len) / 2
        else:
            pattern = self.pattern_var.get()
            if not pattern:
                self._set_status("Enter a pattern (e.g. user%%%%), or switch to Simple mode.", "error")
                return
            if len(pattern) != min_len or len(pattern) != max_len:
                self._set_status(
                    f"Pattern length ({len(pattern)}) must match both Min and Max length "
                    f"({len(pattern)} to {len(pattern)}).", "error")
                return
            charset = self._build_effective_charset() or (CHARSET_LOWER + CHARSET_UPPER + CHARSET_DIGITS)
            wildcards = sum(1 for c in pattern if c in "@,%^")
            if wildcards == 0:
                self._set_status("Pattern has no placeholders (@ , % ^) - it would only produce one fixed word.", "error")
                return
            total = len(charset) ** wildcards
            avg_len = len(pattern)

        if self.permute_var.get() and not self.permute_words_var.get().strip():
            self._set_status("Permutation mode is enabled (Advanced tab) but no words were entered.", "error")
            return

        crunch_path = self.crunch_path_var.get().strip()
        if not crunch_path or not os.path.exists(crunch_path):
            self._set_status("crunch.exe path not found - click Browse to select it.", "error")
            return

        approx_bytes = int(total * (avg_len + 1))
        self._set_status(f"Ready.  Words: {total:,}    Size: {self._human_size(approx_bytes)}", "good")

    @staticmethod
    def _human_size(n):
        for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} EB"

    # ------------------------------------------------------------------
    # Command building
    # ------------------------------------------------------------------
    def _build_command(self):
        crunch_path = self.crunch_path_var.get().strip()
        if not crunch_path or not os.path.exists(crunch_path):
            raise ValueError("crunch.exe path is invalid. Please browse to select it.")

        min_len, max_len = self.min_len_var.get(), self.max_len_var.get()
        if min_len > max_len:
            raise ValueError("Min length cannot be greater than max length.")

        cmd = [crunch_path, str(min_len), str(max_len)]

        if self.mode_var.get() == "charset":
            charset = self._build_effective_charset()
            if not charset:
                raise ValueError("Pick at least one character group, or switch to Pattern mode.")
            cmd.append(charset)
        else:
            pattern = self.pattern_var.get().strip()
            if not pattern:
                raise ValueError("Enter a pattern, or switch to Simple mode.")
            charset = self._build_effective_charset() or (CHARSET_LOWER + CHARSET_UPPER + CHARSET_DIGITS)
            cmd.append(charset)
            cmd += ["-t", pattern]

        output = self.output_var.get().strip()
        if output:
            cmd += ["-o", output]
        if self.split_count_var.get().strip():
            cmd += ["-c", self.split_count_var.get().strip()]
        if self.dup_limit_var.get().strip():
            cmd += ["-d", self.dup_limit_var.get().strip()]
        if self.start_var.get().strip():
            cmd += ["-s", self.start_var.get().strip()]
        if self.end_var.get().strip():
            cmd += ["-e", self.end_var.get().strip()]
        if self.compression_var.get() != "none":
            cmd += ["-z", self.compression_var.get()]
        if self.permute_var.get():
            words = self.permute_words_var.get().strip()
            if not words:
                raise ValueError("Permutation mode is on but no words were given.")
            cmd += ["-p"] + words.split()

        return cmd

    # ------------------------------------------------------------------
    # Run / stop
    # ------------------------------------------------------------------
    def _run_crunch(self):
        try:
            cmd = self._build_command()
        except ValueError as e:
            self._set_status(str(e), "error")
            return

        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self._append_log("Running: " + " ".join(cmd) + "\n\n")

        self.run_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

        def worker():
            try:
                self.process = subprocess.Popen(
                    cmd, cwd=APP_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )
                for line in self.process.stdout:
                    self.log_queue.put(line)
                self.process.wait()
                self.log_queue.put(f"\n[Process finished with exit code {self.process.returncode}]\n")
            except Exception as e:
                self.log_queue.put(f"\n[Error launching crunch: {e}]\n")
            finally:
                self.log_queue.put("__DONE__")

        threading.Thread(target=worker, daemon=True).start()

    def _stop_crunch(self):
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self._append_log("\n[Stopped by user]\n")
            except Exception as e:
                self._append_log(f"\n[Error stopping process: {e}]\n")

    def _append_log(self, text):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _poll_log_queue(self):
        try:
            while True:
                item = self.log_queue.get_nowait()
                if item == "__DONE__":
                    self.run_button.configure(state="normal")
                    self.stop_button.configure(state="disabled")
                else:
                    self._append_log(item)
        except queue.Empty:
            pass
        self.after(100, self._poll_log_queue)


if __name__ == "__main__":
    app = CrunchGUI()
    app.mainloop()