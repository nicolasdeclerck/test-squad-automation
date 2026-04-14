"""Mode texte pour la simulation de tas de sable.

Utile quand Tkinter n'est pas disponible (serveur headless, CI) ou pour
scripter la simulation. Exemple d'usage :

    $ python -m sandpile --cli --rows 5 --cols 5
    > set 2 2 20       # pose 20 grains au centre
    > run              # lance jusqu'à stabilité
    > show             # affiche la grille
    > quit
"""

from __future__ import annotations

import argparse
import shlex
from typing import Optional

from .simulation import MOORE, VON_NEUMANN, Sandpile


HELP = """\
Commandes disponibles :
  show                       afficher la grille
  set   <r> <c> <n>          fixe la case (r, c) à n grains
  add   <r> <c> <n>          ajoute n grains à la case (r, c)
  fill  <n>                  remplit toute la grille avec n grains
  step                       effectue un pas de simulation
  run [max_steps]            exécute jusqu'à stabilité
  reset                      vide la grille
  status                     état (stable ?), nombre de grains
  help                       cette aide
  quit / exit                quitter
"""


def _parse_int(token: str) -> int:
    try:
        return int(token)
    except ValueError as exc:
        raise ValueError(f"entier attendu, reçu : {token!r}") from exc


def _cmd_show(sp: Sandpile) -> None:
    print(sp.to_string())


def _cmd_status(sp: Sandpile) -> None:
    unstable = len(sp.unstable_cells())
    state = "stable" if unstable == 0 else f"{unstable} case(s) instable(s)"
    print(f"Grains totaux : {sp.total_grains()}   État : {state}")


def run_cli(sp: Sandpile) -> None:
    """Boucle interactive REPL."""
    print("Simulation de tas de sable — tapez 'help' pour l'aide, 'quit' pour sortir.")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not line:
            continue
        try:
            tokens = shlex.split(line)
        except ValueError as exc:
            print(f"erreur de parsing : {exc}")
            continue

        cmd, *args = tokens
        cmd = cmd.lower()

        try:
            if cmd in ("quit", "exit"):
                return
            if cmd == "help":
                print(HELP)
            elif cmd == "show":
                _cmd_show(sp)
            elif cmd == "status":
                _cmd_status(sp)
            elif cmd == "set":
                r, c, n = map(_parse_int, args)
                sp[r, c] = n
            elif cmd == "add":
                r, c, n = map(_parse_int, args)
                sp.add(r, c, n=n)
            elif cmd == "fill":
                (n,) = map(_parse_int, args)
                sp.fill(n)
            elif cmd == "step":
                result = sp.step()
                if result.changed:
                    print(f"{len(result.toppled)} case(s) effondrée(s)")
                else:
                    print("grille stable")
            elif cmd == "run":
                max_steps = _parse_int(args[0]) if args else 1_000_000
                steps = sp.run(max_steps=max_steps)
                print(f"stabilité atteinte en {steps} pas")
            elif cmd == "reset":
                sp.reset()
            else:
                print(f"commande inconnue : {cmd!r} (tapez 'help')")
        except (ValueError, IndexError, RuntimeError) as exc:
            print(f"erreur : {exc}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m sandpile",
        description="Simulation d'un tas de sable (Abelian sandpile).",
    )
    parser.add_argument("--rows", type=int, default=15, help="nombre de lignes")
    parser.add_argument("--cols", type=int, default=15, help="nombre de colonnes")
    parser.add_argument(
        "--threshold", type=int, default=8,
        help="seuil strict d'effondrement (défaut : 8)",
    )
    parser.add_argument(
        "--von-neumann", action="store_true",
        help="utilise le voisinage à 4 cases au lieu des 8 de Moore",
    )
    parser.add_argument(
        "--cli", action="store_true",
        help="lance le mode texte interactif au lieu de la GUI Tkinter",
    )
    parser.add_argument(
        "--cell-size", type=int, default=36,
        help="taille d'une case en pixels dans la GUI (défaut : 36)",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    neighborhood = VON_NEUMANN if args.von_neumann else MOORE

    if args.cli:
        sp = Sandpile(
            rows=args.rows, cols=args.cols,
            threshold=args.threshold, neighborhood=neighborhood,
        )
        run_cli(sp)
        return 0

    try:
        from .gui import SandpileGUI
    except ImportError as exc:  # pragma: no cover - tkinter absent
        print(f"Tkinter indisponible ({exc}). Relancez avec --cli.")
        return 1

    SandpileGUI(
        rows=args.rows, cols=args.cols,
        threshold=args.threshold,
        moore=not args.von_neumann,
        cell_size=args.cell_size,
    ).mainloop()
    return 0
