"""Interface graphique Tkinter pour la simulation de tas de sable.

Utilisation :

    python -m sandpile              # lance la GUI (par défaut)
    python -m sandpile --cli        # mode texte

Commandes dans la GUI :
- Clic gauche           : ajoute ``N`` grains (valeur du champ "grains/clic")
- Clic droit            : retire ``N`` grains (min 0)
- Shift + clic gauche   : pose exactement ``N`` grains dans la case
- Boutons               : ``Pas à pas``, ``Lancer``, ``Pause``, ``Reset``,
                          ``Remplir``
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from .simulation import MOORE, VON_NEUMANN, Sandpile


# Palette — du vert clair (peu de grains) au rouge (saturé) et violet (instable).
_PALETTE = [
    "#f5f5f5",  # 0
    "#e3f6e3",  # 1
    "#c8edc8",  # 2
    "#a6e0a6",  # 3
    "#7fd17f",  # 4
    "#f4d35e",  # 5
    "#ee964b",  # 6
    "#f3722c",  # 7
    "#d00000",  # 8 (max stable)
]
_UNSTABLE_COLOR = "#6a0572"  # > 8


def _color_for(value: int) -> str:
    if value <= 0:
        return _PALETTE[0]
    if value < len(_PALETTE):
        return _PALETTE[value]
    return _UNSTABLE_COLOR


class SandpileGUI:
    """Fenêtre principale de l'application."""

    def __init__(
        self,
        rows: int = 15,
        cols: int = 15,
        cell_size: int = 36,
        threshold: int = 8,
        moore: bool = True,
    ) -> None:
        self.cell_size = cell_size
        neighborhood = MOORE if moore else VON_NEUMANN
        self.sandpile = Sandpile(rows, cols, threshold=threshold,
                                 neighborhood=neighborhood)

        self.root = tk.Tk()
        self.root.title("Tas de sable — simulation")
        self.root.resizable(False, False)

        self._build_controls()
        self._build_canvas()
        self._build_status_bar()

        self._running = False
        self._after_id: Optional[str] = None
        self._step_count = 0

        self._redraw_all()
        self._update_status()

    # ------------------------------------------------------------- UI setup

    def _build_controls(self) -> None:
        frame = ttk.Frame(self.root, padding=8)
        frame.grid(row=0, column=0, sticky="ew")

        ttk.Label(frame, text="Grains / clic :").grid(row=0, column=0, padx=(0, 4))
        self.grains_var = tk.IntVar(value=4)
        ttk.Spinbox(
            frame, from_=1, to=99, width=4, textvariable=self.grains_var
        ).grid(row=0, column=1, padx=(0, 12))

        ttk.Label(frame, text="Vitesse (ms) :").grid(row=0, column=2, padx=(0, 4))
        self.speed_var = tk.IntVar(value=80)
        ttk.Spinbox(
            frame, from_=0, to=2000, increment=20, width=5,
            textvariable=self.speed_var,
        ).grid(row=0, column=3, padx=(0, 12))

        ttk.Button(frame, text="Pas à pas", command=self.step_once).grid(
            row=0, column=4, padx=2
        )
        self.run_button = ttk.Button(frame, text="Lancer", command=self.toggle_run)
        self.run_button.grid(row=0, column=5, padx=2)

        ttk.Button(frame, text="Reset", command=self.reset).grid(
            row=0, column=6, padx=2
        )
        ttk.Button(frame, text="Remplir…", command=self.fill_dialog).grid(
            row=0, column=7, padx=2
        )

    def _build_canvas(self) -> None:
        width = self.sandpile.cols * self.cell_size
        height = self.sandpile.rows * self.cell_size
        self.canvas = tk.Canvas(
            self.root, width=width, height=height,
            background="#ffffff", highlightthickness=0,
        )
        self.canvas.grid(row=1, column=0, padx=8, pady=(0, 8))

        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.canvas.bind("<Shift-Button-1>", self._on_shift_left_click)

        # Rectangles + texte pré-créés pour être rapides à mettre à jour.
        self._rects: list[list[int]] = []
        self._texts: list[list[int]] = []
        for r in range(self.sandpile.rows):
            row_rects = []
            row_texts = []
            for c in range(self.sandpile.cols):
                x0 = c * self.cell_size
                y0 = r * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                rect = self.canvas.create_rectangle(
                    x0, y0, x1, y1,
                    fill=_PALETTE[0], outline="#cccccc",
                )
                text = self.canvas.create_text(
                    x0 + self.cell_size / 2,
                    y0 + self.cell_size / 2,
                    text="", font=("TkDefaultFont", 10, "bold"),
                )
                row_rects.append(rect)
                row_texts.append(text)
            self._rects.append(row_rects)
            self._texts.append(row_texts)

    def _build_status_bar(self) -> None:
        self.status_var = tk.StringVar()
        bar = ttk.Label(
            self.root, textvariable=self.status_var, anchor="w", padding=(8, 4)
        )
        bar.grid(row=2, column=0, sticky="ew")

    # -------------------------------------------------------- événements UI

    def _cell_from_event(self, event: tk.Event) -> Optional[tuple[int, int]]:
        c = event.x // self.cell_size
        r = event.y // self.cell_size
        if self.sandpile.in_bounds(r, c):
            return r, c
        return None

    def _on_left_click(self, event: tk.Event) -> None:
        cell = self._cell_from_event(event)
        if cell is None:
            return
        self.sandpile.add(*cell, n=self.grains_var.get())
        self._redraw_cell(*cell)
        self._update_status()

    def _on_right_click(self, event: tk.Event) -> None:
        cell = self._cell_from_event(event)
        if cell is None:
            return
        r, c = cell
        current = self.sandpile[r, c]
        delta = min(self.grains_var.get(), current)
        if delta:
            self.sandpile.add(r, c, n=-delta)
            self._redraw_cell(r, c)
            self._update_status()

    def _on_shift_left_click(self, event: tk.Event) -> None:
        cell = self._cell_from_event(event)
        if cell is None:
            return
        self.sandpile[cell] = self.grains_var.get()
        self._redraw_cell(*cell)
        self._update_status()

    # ------------------------------------------------------------ actions

    def step_once(self) -> None:
        result = self.sandpile.step()
        if result.changed:
            self._step_count += 1
            self._redraw_all()
        self._update_status()

    def toggle_run(self) -> None:
        if self._running:
            self._stop()
        else:
            self._start()

    def _start(self) -> None:
        if self.sandpile.is_stable():
            return
        self._running = True
        self.run_button.config(text="Pause")
        self._schedule_tick()

    def _stop(self) -> None:
        self._running = False
        self.run_button.config(text="Lancer")
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)
            self._after_id = None

    def _schedule_tick(self) -> None:
        delay = max(0, self.speed_var.get())
        self._after_id = self.root.after(delay, self._tick)

    def _tick(self) -> None:
        self._after_id = None
        if not self._running:
            return
        result = self.sandpile.step()
        if result.changed:
            self._step_count += 1
            self._redraw_all()
            self._update_status()
            self._schedule_tick()
        else:
            self._stop()
            self._update_status()

    def reset(self) -> None:
        self._stop()
        self.sandpile.reset()
        self._step_count = 0
        self._redraw_all()
        self._update_status()

    def fill_dialog(self) -> None:
        self._stop()
        dialog = tk.Toplevel(self.root)
        dialog.title("Remplir la grille")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Grains par case :").grid(
            row=0, column=0, padx=8, pady=8
        )
        value_var = tk.IntVar(value=4)
        ttk.Spinbox(
            dialog, from_=0, to=999, width=6, textvariable=value_var
        ).grid(row=0, column=1, padx=8, pady=8)

        def apply_fill() -> None:
            try:
                self.sandpile.fill(value_var.get())
            except ValueError as exc:
                messagebox.showerror("Valeur invalide", str(exc), parent=dialog)
                return
            self._step_count = 0
            self._redraw_all()
            self._update_status()
            dialog.destroy()

        ttk.Button(dialog, text="Appliquer", command=apply_fill).grid(
            row=1, column=0, columnspan=2, pady=(0, 8)
        )

    # ---------------------------------------------------------- rendering

    def _redraw_cell(self, r: int, c: int) -> None:
        value = self.sandpile[r, c]
        self.canvas.itemconfig(self._rects[r][c], fill=_color_for(value))
        label = str(value) if value else ""
        fg = "#ffffff" if value >= 5 else "#333333"
        self.canvas.itemconfig(self._texts[r][c], text=label, fill=fg)

    def _redraw_all(self) -> None:
        for r in range(self.sandpile.rows):
            for c in range(self.sandpile.cols):
                self._redraw_cell(r, c)

    def _update_status(self) -> None:
        unstable = len(self.sandpile.unstable_cells())
        state = "stable" if unstable == 0 else f"{unstable} case(s) instable(s)"
        self.status_var.set(
            f"Pas : {self._step_count}   "
            f"Grains : {self.sandpile.total_grains()}   "
            f"État : {state}"
        )

    # ------------------------------------------------------------- lancement

    def mainloop(self) -> None:
        self.root.mainloop()


def run_gui(**kwargs) -> None:
    """Point d'entrée pratique pour lancer la GUI."""
    SandpileGUI(**kwargs).mainloop()
