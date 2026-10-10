# SPDX-License-Identifier: MIT
"""
Simple graphical interface for MarkItDown.

Launch with ``markitdown-gui`` or ``python -m markitdown._gui``.
Uses only tkinter (bundled with Python). Drag & drop is enabled automatically
when the optional ``tkinterdnd2`` package is installed (``pip install markitdown[gui]``).
"""
import locale
import queue
import threading
from pathlib import Path
from typing import Dict, List, Tuple

from .__about__ import __version__

_STRINGS = {
    "en": {
        "title": "MarkItDown",
        "add": "Add files…",
        "clear": "Clear",
        "convert": "Convert",
        "copy": "Copy",
        "save": "Save as .md…",
        "save_all": "Save all…",
        "drop": "Drag files here, or click “Add files…”",
        "drop_plain": "Click “Add files…” to choose the documents to convert",
        "ready": "Ready.",
        "converting": "Converting {i}/{n}: {name}",
        "done": "Done: {ok} converted, {bad} failed.",
        "copied": "Copied to clipboard.",
        "saved": "Saved: {path}",
        "saved_n": "Saved {n} files in {path}",
        "pick_folder": "Choose the folder to save the .md files",
        "all_files": "All files",
        "err_missing": "Missing optional dependency for this format.\nInstall it with:  pip install \"markitdown[all]\"",
        "err_unsupported": "This file format is not supported.",
        "err_notfound": "The file was not found.",
        "err_other": "Could not convert this file: {msg}",
    },
    "es": {
        "title": "MarkItDown",
        "add": "Agregar archivos…",
        "clear": "Limpiar",
        "convert": "Convertir",
        "copy": "Copiar",
        "save": "Guardar como .md…",
        "save_all": "Guardar todo…",
        "drop": "Arrastra archivos aquí o pulsa «Agregar archivos…»",
        "drop_plain": "Pulsa «Agregar archivos…» para elegir los documentos a convertir",
        "ready": "Listo.",
        "converting": "Convirtiendo {i}/{n}: {name}",
        "done": "Terminado: {ok} convertidos, {bad} con error.",
        "copied": "Copiado al portapapeles.",
        "saved": "Guardado: {path}",
        "saved_n": "Se guardaron {n} archivos en {path}",
        "pick_folder": "Elige la carpeta donde guardar los .md",
        "all_files": "Todos los archivos",
        "err_missing": "Falta una dependencia opcional para este formato.\nInstálala con:  pip install \"markitdown[all]\"",
        "err_unsupported": "Este formato de archivo no es compatible.",
        "err_notfound": "No se encontró el archivo.",
        "err_other": "No se pudo convertir este archivo: {msg}",
    },
}


def _detect_lang() -> str:
    try:
        code = (locale.getlocale()[0] or "").lower()
    except Exception:
        code = ""
    return "es" if code.startswith("es") else "en"


def convert_path(path: str, md=None) -> Tuple[bool, str]:
    """Convert one file. Returns (ok, markdown_or_friendly_error). Never raises."""
    from ._exceptions import (
        MissingDependencyException,
        UnsupportedFormatException,
        FileConversionException,
    )
    from ._markitdown import MarkItDown

    s = _STRINGS[_detect_lang()]
    try:
        md = md or MarkItDown()
        return True, md.convert(path).markdown
    except FileNotFoundError:
        return False, s["err_notfound"]
    except UnsupportedFormatException:
        return False, s["err_unsupported"]
    except MissingDependencyException:
        return False, s["err_missing"]
    except FileConversionException as e:
        text = str(e)
        if "dependencies needed" in text or "MissingDependency" in text:
            return False, s["err_missing"]
        return False, s["err_other"].format(msg=text.splitlines()[0] if text else e)
    except Exception as e:  # pragma: no cover - defensive
        return False, s["err_other"].format(msg=e)


def unique_md_path(folder: Path, source: str) -> Path:
    """<folder>/<name>.md, adding -1, -2… if it already exists."""
    stem = Path(source).stem
    target = folder / f"{stem}.md"
    n = 1
    while target.exists():
        target = folder / f"{stem}-{n}.md"
        n += 1
    return target


def main() -> None:
    import tkinter as tk
    from tkinter import filedialog, ttk

    try:
        from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore

        root = TkinterDnD.Tk()
        has_dnd = True
    except Exception:
        root = tk.Tk()
        has_dnd = False

    s = _STRINGS[_detect_lang()]
    root.title(f"{s['title']} {__version__}")
    root.geometry("860x600")
    root.minsize(640, 420)

    files: List[str] = []
    results: Dict[str, Tuple[bool, str]] = {}
    events: "queue.Queue" = queue.Queue()
    status = tk.StringVar(value=s["ready"])

    # ---- layout ---------------------------------------------------------
    top = ttk.Frame(root, padding=8)
    top.pack(fill="x")
    btn_add = ttk.Button(top, text=s["add"])
    btn_clear = ttk.Button(top, text=s["clear"])
    btn_convert = ttk.Button(top, text=s["convert"])
    for b in (btn_add, btn_clear, btn_convert):
        b.pack(side="left", padx=(0, 6))

    body = ttk.PanedWindow(root, orient="horizontal")
    body.pack(fill="both", expand=True, padx=8)

    left = ttk.Frame(body)
    listbox = tk.Listbox(left, activestyle="none", exportselection=False, width=30)
    listbox.pack(fill="both", expand=True)
    hint = ttk.Label(
        left, text=s["drop"] if has_dnd else s["drop_plain"], wraplength=220, foreground="#666"
    )
    hint.pack(fill="x", pady=(6, 0))
    body.add(left, weight=1)

    right = ttk.Frame(body)
    text = tk.Text(right, wrap="word", undo=False)
    scroll = ttk.Scrollbar(right, command=text.yview)
    text.configure(yscrollcommand=scroll.set, state="disabled")
    scroll.pack(side="right", fill="y")
    text.pack(side="left", fill="both", expand=True)
    body.add(right, weight=3)

    bottom = ttk.Frame(root, padding=8)
    bottom.pack(fill="x")
    btn_copy = ttk.Button(bottom, text=s["copy"])
    btn_save = ttk.Button(bottom, text=s["save"])
    btn_save_all = ttk.Button(bottom, text=s["save_all"])
    for b in (btn_copy, btn_save, btn_save_all):
        b.pack(side="left", padx=(0, 6))
    ttk.Label(bottom, textvariable=status).pack(side="right")

    # ---- helpers --------------------------------------------------------
    def set_text(value: str) -> None:
        text.configure(state="normal")
        text.delete("1.0", "end")
        text.insert("1.0", value)
        text.configure(state="disabled")

    def refresh_state() -> None:
        has_files = bool(files)
        has_ok = any(ok for ok, _ in results.values())
        btn_convert.state(["!disabled"] if has_files else ["disabled"])
        btn_clear.state(["!disabled"] if has_files else ["disabled"])
        for b in (btn_copy, btn_save, btn_save_all):
            b.state(["!disabled"] if has_ok else ["disabled"])

    def add_files(paths) -> None:
        for p in paths:
            p = str(p)
            if p and p not in files and Path(p).is_file():
                files.append(p)
                listbox.insert("end", Path(p).name)
        refresh_state()

    def current() -> str:
        sel = listbox.curselection()
        return files[sel[0]] if sel else ""

    def show_selected(_evt=None) -> None:
        path = current()
        if path in results:
            set_text(results[path][1])

    # ---- actions --------------------------------------------------------
    def on_add() -> None:
        chosen = filedialog.askopenfilenames(
            title=s["add"], filetypes=[(s["all_files"], "*.*")]
        )
        add_files(chosen)

    def on_clear() -> None:
        files.clear()
        results.clear()
        listbox.delete(0, "end")
        set_text("")
        status.set(s["ready"])
        refresh_state()

    def worker(paths: List[str]) -> None:
        from ._markitdown import MarkItDown

        md = MarkItDown()
        for i, p in enumerate(paths, 1):
            events.put(("progress", i, len(paths), Path(p).name))
            events.put(("result", p, convert_path(p, md)))
        events.put(("done",))

    def on_convert() -> None:
        if not files:
            return
        btn_convert.state(["disabled"])
        results.clear()
        threading.Thread(target=worker, args=(list(files),), daemon=True).start()

    def poll() -> None:
        try:
            while True:
                ev = events.get_nowait()
                if ev[0] == "progress":
                    status.set(s["converting"].format(i=ev[1], n=ev[2], name=ev[3]))
                elif ev[0] == "result":
                    results[ev[1]] = ev[2]
                    idx = files.index(ev[1])
                    listbox.itemconfig(idx, foreground="#000" if ev[2][0] else "#b00020")
                    if len(results) == 1:
                        listbox.selection_clear(0, "end")
                        listbox.selection_set(idx)
                        show_selected()
                elif ev[0] == "done":
                    ok = sum(1 for o, _ in results.values() if o)
                    status.set(s["done"].format(ok=ok, bad=len(results) - ok))
                    refresh_state()
                    btn_convert.state(["!disabled"])
        except queue.Empty:
            pass
        root.after(100, poll)

    def on_copy() -> None:
        root.clipboard_clear()
        root.clipboard_append(text.get("1.0", "end-1c"))
        status.set(s["copied"])

    def on_save() -> None:
        path = current()
        if path not in results or not results[path][0]:
            return
        target = filedialog.asksaveasfilename(
            defaultextension=".md",
            initialfile=Path(path).stem + ".md",
            initialdir=str(Path(path).parent),
            filetypes=[("Markdown", "*.md")],
        )
        if target:
            Path(target).write_text(results[path][1], encoding="utf-8")
            status.set(s["saved"].format(path=target))

    def on_save_all() -> None:
        folder = filedialog.askdirectory(title=s["pick_folder"])
        if not folder:
            return
        n = 0
        for p, (ok, content) in results.items():
            if ok:
                unique_md_path(Path(folder), p).write_text(content, encoding="utf-8")
                n += 1
        status.set(s["saved_n"].format(n=n, path=folder))

    btn_add.configure(command=on_add)
    btn_clear.configure(command=on_clear)
    btn_convert.configure(command=on_convert)
    btn_copy.configure(command=on_copy)
    btn_save.configure(command=on_save)
    btn_save_all.configure(command=on_save_all)
    listbox.bind("<<ListboxSelect>>", show_selected)

    if has_dnd:
        for widget in (listbox, text, hint):
            widget.drop_target_register(DND_FILES)  # type: ignore[attr-defined]
            widget.dnd_bind(  # type: ignore[attr-defined]
                "<<Drop>>", lambda e: add_files(root.tk.splitlist(e.data))
            )

    refresh_state()
    root.after(100, poll)
    root.mainloop()


if __name__ == "__main__":
    main()
