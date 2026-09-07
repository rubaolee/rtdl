"""Route-independent exact tetrahedron point-location oracle.

The oracle uses rational arithmetic and imports no author, V2, V3 or V4 code.
It is evidence for the selected application's output contract, not a substitute
for behavioral OptiX execution.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Iterable, Sequence


Point = tuple[Fraction, Fraction, Fraction]
Cell = tuple[int, int, int, int]


def point(x: int | Fraction, y: int | Fraction, z: int | Fraction) -> Point:
    return Fraction(x), Fraction(y), Fraction(z)


def _sub(a: Point, b: Point) -> Point:
    return a[0] - b[0], a[1] - b[1], a[2] - b[2]


def _det(a: Point, b: Point, c: Point) -> Fraction:
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def barycentric(point_value: Point, vertices: Sequence[Point], cell: Cell) -> tuple[Fraction, ...]:
    a, b, c, d = (vertices[index] for index in cell)
    denominator = _det(_sub(a, d), _sub(b, d), _sub(c, d))
    if denominator == 0:
        raise ValueError("degenerate tetrahedron")
    wa = _det(_sub(point_value, d), _sub(b, d), _sub(c, d)) / denominator
    wb = _det(_sub(a, d), _sub(point_value, d), _sub(c, d)) / denominator
    wc = _det(_sub(a, d), _sub(b, d), _sub(point_value, d)) / denominator
    wd = Fraction(1) - wa - wb - wc
    return wa, wb, wc, wd


def containing_cells(
    point_value: Point,
    vertices: Sequence[Point],
    cells: Sequence[Cell],
) -> tuple[int, ...]:
    matches = []
    for cell_id, cell in enumerate(cells):
        weights = barycentric(point_value, vertices, cell)
        if all(weight >= 0 for weight in weights):
            matches.append(cell_id)
    return tuple(matches)


def locate_cell(
    point_value: Point,
    vertices: Sequence[Point],
    cells: Sequence[Cell],
) -> int:
    """Return unique cell ID; reject ambiguous boundary or outside inputs."""

    matches = containing_cells(point_value, vertices, cells)
    if len(matches) != 1:
        raise ValueError(f"point-location is not unique: matches={matches}")
    return matches[0]


def two_tetra_fixture() -> tuple[tuple[Point, ...], tuple[Cell, ...]]:
    # Two tetrahedra share face (1, 2, 3) and lie on opposite sides.
    vertices = (
        point(0, 0, 0),
        point(1, 0, 0),
        point(0, 1, 0),
        point(0, 0, 1),
        point(1, 1, 1),
    )
    cells = ((0, 1, 2, 3), (4, 1, 2, 3))
    return vertices, cells
