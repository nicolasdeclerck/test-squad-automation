"""Tests unitaires pour la simulation de tas de sable."""

from __future__ import annotations

import pytest

from sandpile.simulation import MOORE, VON_NEUMANN, Sandpile


class TestConstruction:
    def test_default_values(self):
        sp = Sandpile(3, 4)
        assert sp.rows == 3
        assert sp.cols == 4
        assert sp.threshold == 8
        assert sp.neighborhood == MOORE
        assert sp.total_grains() == 0
        assert sp.is_stable()

    @pytest.mark.parametrize(
        "rows,cols", [(0, 3), (3, 0), (-1, 2), (2, -1)]
    )
    def test_invalid_dimensions(self, rows, cols):
        with pytest.raises(ValueError):
            Sandpile(rows, cols)

    def test_invalid_threshold(self):
        with pytest.raises(ValueError):
            Sandpile(3, 3, threshold=-1)


class TestMutations:
    def test_add_and_get(self):
        sp = Sandpile(3, 3)
        sp.add(1, 1, 5)
        assert sp[1, 1] == 5
        sp.add(1, 1, 3)
        assert sp[1, 1] == 8

    def test_add_negative_cannot_go_below_zero(self):
        sp = Sandpile(3, 3)
        sp.add(0, 0, 3)
        with pytest.raises(ValueError):
            sp.add(0, 0, -10)

    def test_set_rejects_negative(self):
        sp = Sandpile(3, 3)
        with pytest.raises(ValueError):
            sp[0, 0] = -1

    def test_add_out_of_bounds(self):
        sp = Sandpile(3, 3)
        with pytest.raises(IndexError):
            sp.add(3, 0, 1)

    def test_fill_and_reset(self):
        sp = Sandpile(2, 2)
        sp.fill(7)
        assert sp.total_grains() == 28
        assert sp.is_stable()
        sp.reset()
        assert sp.total_grains() == 0


class TestNeighbors:
    def test_moore_interior_has_8(self):
        sp = Sandpile(5, 5)
        assert len(sp.neighbors(2, 2)) == 8

    def test_moore_corner_has_3(self):
        sp = Sandpile(5, 5)
        assert sorted(sp.neighbors(0, 0)) == [(0, 1), (1, 0), (1, 1)]

    def test_moore_edge_has_5(self):
        sp = Sandpile(5, 5)
        assert len(sp.neighbors(0, 2)) == 5

    def test_von_neumann_interior_has_4(self):
        sp = Sandpile(5, 5, neighborhood=VON_NEUMANN)
        assert len(sp.neighbors(2, 2)) == 4


class TestStep:
    def test_stable_grid_does_not_change(self):
        sp = Sandpile(3, 3)
        sp.fill(8)  # pile à la limite mais stable
        before = [row[:] for row in sp.grid]
        result = sp.step()
        assert not result.changed
        assert result.toppled == []
        assert sp.grid == before

    def test_single_topple_in_center(self):
        sp = Sandpile(3, 3)
        sp[1, 1] = 9
        result = sp.step()
        assert result.changed
        assert result.toppled == [(1, 1)]
        # La case centrale a 8 voisins -> elle perd 8 grains (il en reste 1).
        assert sp[1, 1] == 1
        # Chaque voisin reçoit 1 grain.
        for r in range(3):
            for c in range(3):
                if (r, c) != (1, 1):
                    assert sp[r, c] == 1
        assert sp.total_grains() == 9  # conservation

    def test_corner_cell_only_loses_three_grains(self):
        """Un coin n'a que 3 voisins : il ne perd que 3 grains."""
        sp = Sandpile(3, 3)
        sp[0, 0] = 9
        result = sp.step()
        assert result.toppled == [(0, 0)]
        assert sp[0, 0] == 9 - 3  # conserve les grains non distribuables
        assert sp[0, 1] == 1
        assert sp[1, 0] == 1
        assert sp[1, 1] == 1
        assert sp.total_grains() == 9  # conservation des grains

    def test_simultaneous_topple(self):
        """Deux cases instables s'effondrent en un seul pas."""
        sp = Sandpile(5, 5)
        sp[1, 1] = 9
        sp[3, 3] = 9
        result = sp.step()
        assert set(result.toppled) == {(1, 1), (3, 3)}
        assert sp[1, 1] == 1
        assert sp[3, 3] == 1
        # Les voisinages ne se chevauchent pas pour ces coordonnées.
        assert sp[2, 2] == 2  # voisin des deux cases -> reçoit 2
        assert sp.total_grains() == 18


class TestRun:
    def test_stable_run_returns_zero_steps(self):
        sp = Sandpile(3, 3)
        sp.fill(2)
        assert sp.run() == 0

    def test_cascade_reaches_stability(self):
        sp = Sandpile(5, 5)
        sp[2, 2] = 50
        steps = sp.run()
        assert steps > 0
        assert sp.is_stable()
        # Conservation : Moore à l'intérieur = aucun grain ne sort.
        # Les grains restent tous dans la grille.
        assert sp.total_grains() == 50

    def test_run_respects_max_steps(self):
        sp = Sandpile(5, 5)
        sp[2, 2] = 100
        with pytest.raises(RuntimeError):
            sp.run(max_steps=1)

    def test_abelian_property(self):
        """L'ordre des ajouts ne doit pas changer l'état stable final."""
        sp1 = Sandpile(7, 7)
        sp1.add(3, 3, 20)
        sp1.add(2, 4, 15)
        sp1.run()

        sp2 = Sandpile(7, 7)
        sp2.add(2, 4, 15)
        sp2.add(3, 3, 20)
        sp2.run()

        assert sp1.grid == sp2.grid

    def test_von_neumann_classical_sandpile(self):
        """Sandpile classique : threshold 4, voisinage 4 cases."""
        sp = Sandpile(5, 5, threshold=3, neighborhood=VON_NEUMANN)
        sp[2, 2] = 4
        steps = sp.run()
        assert steps >= 1
        assert sp.is_stable()
        assert sp[2, 2] == 0
        assert sp[1, 2] == 1
        assert sp[3, 2] == 1
        assert sp[2, 1] == 1
        assert sp[2, 3] == 1


class TestSerialization:
    def test_to_string_shape(self):
        sp = Sandpile(2, 3)
        sp[0, 0] = 1
        sp[1, 2] = 12
        out = sp.to_string(width=3)
        lines = out.split("\n")
        assert len(lines) == 2
        assert all(len(line) == 9 for line in lines)
        assert "12" in lines[1]
