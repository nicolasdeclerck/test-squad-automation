"""Sandpile simulation package.

Exercice mathématique : simulation d'un tas de sable (Abelian sandpile model)
sur une grille. Lorsqu'une case contient strictement plus de 8 grains, elle
distribue un grain à chacune de ses cases adjacentes (voisinage de Moore),
et l'on recommence jusqu'à ce que plus aucune case ne puisse s'effondrer.
"""

from .simulation import Sandpile, MOORE, VON_NEUMANN

__all__ = ["Sandpile", "MOORE", "VON_NEUMANN"]
