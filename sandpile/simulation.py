"""Cœur de la simulation de tas de sable.

Règles implémentées par défaut :
- Grille rectangulaire de taille ``rows x cols``.
- Toute case contenant strictement plus de ``threshold`` grains (par défaut 8)
  est dite instable et "s'effondre" : elle distribue un grain à chacune de ses
  cases adjacentes (voisinage de Moore à 8 cases par défaut).
- Une case en bordure ou en coin possède moins de voisins ; elle ne perd donc
  que le nombre de grains effectivement distribués (les grains "perdus dans le
  vide" ne sont pas modélisés ici — conformément à l'énoncé, on met un grain
  dans chaque case adjacente, point).
- On répète jusqu'à ce que plus aucune case ne dépasse le seuil.

L'implémentation est pure (aucune dépendance externe) et testable isolément.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Tuple

MOORE: Tuple[Tuple[int, int], ...] = (
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
)

VON_NEUMANN: Tuple[Tuple[int, int], ...] = (
    (-1, 0), (1, 0), (0, -1), (0, 1),
)


Cell = Tuple[int, int]


@dataclass
class StepResult:
    """Résultat d'un pas de simulation."""

    toppled: List[Cell] = field(default_factory=list)
    changed: bool = False


class Sandpile:
    """Grille de tas de sable.

    :param rows: nombre de lignes.
    :param cols: nombre de colonnes.
    :param threshold: seuil strict au-delà duquel une case s'effondre.
        Par défaut 8 — une case avec 9 grains ou plus est instable.
    :param neighborhood: itérable de couples ``(dr, dc)`` décrivant le
        voisinage. ``MOORE`` (8 voisins) par défaut ; ``VON_NEUMANN`` pour
        l'abelian sandpile classique à 4 voisins.
    """

    def __init__(
        self,
        rows: int,
        cols: int,
        threshold: int = 8,
        neighborhood: Iterable[Tuple[int, int]] = MOORE,
    ) -> None:
        if rows <= 0 or cols <= 0:
            raise ValueError("rows et cols doivent être strictement positifs")
        if threshold < 0:
            raise ValueError("threshold doit être positif ou nul")

        self.rows = rows
        self.cols = cols
        self.threshold = threshold
        self.neighborhood: Tuple[Tuple[int, int], ...] = tuple(neighborhood)
        self.grid: List[List[int]] = [[0] * cols for _ in range(rows)]

    # ------------------------------------------------------------------ accès

    def __getitem__(self, pos: Cell) -> int:
        r, c = pos
        return self.grid[r][c]

    def __setitem__(self, pos: Cell, value: int) -> None:
        r, c = pos
        if value < 0:
            raise ValueError("le nombre de grains doit être positif")
        self.grid[r][c] = value

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    def neighbors(self, r: int, c: int) -> List[Cell]:
        return [
            (r + dr, c + dc)
            for dr, dc in self.neighborhood
            if self.in_bounds(r + dr, c + dc)
        ]

    # ------------------------------------------------------------- mutations

    def add(self, r: int, c: int, n: int = 1) -> None:
        """Ajoute ``n`` grains dans la case ``(r, c)``."""
        if not self.in_bounds(r, c):
            raise IndexError(f"case hors-grille : ({r}, {c})")
        new_value = self.grid[r][c] + n
        if new_value < 0:
            raise ValueError("le nombre de grains ne peut pas devenir négatif")
        self.grid[r][c] = new_value

    def fill(self, value: int) -> None:
        """Remplit toutes les cases avec ``value`` grains."""
        if value < 0:
            raise ValueError("value doit être positif ou nul")
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = value

    def reset(self) -> None:
        """Vide complètement la grille."""
        self.fill(0)

    # ------------------------------------------------------------- simulation

    def unstable_cells(self) -> List[Cell]:
        """Retourne la liste des cases instables (strictement > seuil)."""
        return [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if self.grid[r][c] > self.threshold
        ]

    def is_stable(self) -> bool:
        """``True`` si aucune case ne dépasse le seuil."""
        for row in self.grid:
            for value in row:
                if value > self.threshold:
                    return False
        return True

    def total_grains(self) -> int:
        return sum(sum(row) for row in self.grid)

    def step(self) -> StepResult:
        """Effectue un pas de simulation (effondrement simultané).

        Toutes les cases instables s'effondrent en parallèle : chacune envoie
        un grain à chaque voisin dans la grille et perd autant de grains
        qu'elle a de voisins. Les effondrements provoqués en cascade se
        produiront au pas suivant.

        Retourne un :class:`StepResult` précisant quelles cases se sont
        effondrées et si la grille a changé.
        """
        to_topple = self.unstable_cells()
        if not to_topple:
            return StepResult(toppled=[], changed=False)

        deltas: List[List[int]] = [[0] * self.cols for _ in range(self.rows)]
        for r, c in to_topple:
            neigh = self.neighbors(r, c)
            deltas[r][c] -= len(neigh)
            for nr, nc in neigh:
                deltas[nr][nc] += 1

        for r in range(self.rows):
            for c in range(self.cols):
                if deltas[r][c]:
                    self.grid[r][c] += deltas[r][c]

        return StepResult(toppled=to_topple, changed=True)

    def run(self, max_steps: int = 1_000_000) -> int:
        """Exécute la simulation jusqu'à stabilité (ou ``max_steps`` pas).

        Retourne le nombre de pas effectués. Lève :class:`RuntimeError` si
        ``max_steps`` est atteint sans stabilisation (ne devrait pas arriver
        pour un nombre fini de grains sur une grille bornée).
        """
        steps = 0
        while True:
            result = self.step()
            if not result.changed:
                return steps
            steps += 1
            if steps >= max_steps:
                raise RuntimeError(
                    f"La simulation n'a pas convergé en {max_steps} pas."
                )

    # ------------------------------------------------------------- affichage

    def to_string(self, width: int = 3) -> str:
        """Représentation texte de la grille (utile pour CLI et tests)."""
        return "\n".join(
            "".join(f"{value:>{width}}" for value in row) for row in self.grid
        )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return (
            f"Sandpile(rows={self.rows}, cols={self.cols}, "
            f"threshold={self.threshold}, total={self.total_grains()})"
        )
