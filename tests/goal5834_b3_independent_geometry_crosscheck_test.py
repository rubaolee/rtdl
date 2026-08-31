"""Second algorithmic cross-check of the frozen B1/B3 geometry rows."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from examples.curve_boolean_contact.fixtures import (  # noqa: E402
    build_evaluation_manifest,
)


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _distance2_at(p, u, q, v, s, t):
    delta = tuple(p[i] + s * u[i] - q[i] - t * v[i] for i in range(3))
    return _dot(delta, delta)


def independent_active_set_distance2(first_start, first_end, second_start,
                                     second_end):
    """Minimize the convex two-parameter quadratic by active-set enumeration."""
    p, q = first_start, second_start
    u, v = _sub(first_end, first_start), _sub(second_end, second_start)
    w = _sub(p, q)
    a, b, c = _dot(u, u), _dot(u, v), _dot(v, v)
    d, e = _dot(u, w), _dot(v, w)
    clamp = lambda value: max(0.0, min(1.0, value))
    candidates = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]
    if c > 0.0:
        candidates.extend(((0.0, clamp(e / c)),
                           (1.0, clamp((e + b) / c))))
    if a > 0.0:
        candidates.extend(((clamp(-d / a), 0.0),
                           (clamp((b - d) / a), 1.0)))
    determinant = a * c - b * b
    if determinant > 0.0:
        s = (b * e - c * d) / determinant
        t = (a * e - b * d) / determinant
        if 0.0 <= s <= 1.0 and 0.0 <= t <= 1.0:
            candidates.append((s, t))
    return min(_distance2_at(p, u, q, v, s, t) for s, t in candidates)


class Goal5834B3IndependentGeometryCrosscheckTest(unittest.TestCase):
    def test_all_frozen_pair_distances_and_bits_recompute(self):
        manifest = build_evaluation_manifest()
        checked = 0
        for fixture in manifest["executable"]:
            capsules = fixture["normalization"]["capsules"]
            queries = fixture["normalization"]["queries"]
            rows = fixture["canonical_oracle"]["pair_rows"]
            by_pair = {(row["query_index"], row["capsule_index"]): row
                       for row in rows}
            second_bits = []
            for query_index, (query_start, query_end) in enumerate(queries):
                hit = False
                for capsule_index, (start, end, radius, _identity) in enumerate(
                        capsules):
                    distance2 = independent_active_set_distance2(
                        query_start, query_end, start, end)
                    first = by_pair[(query_index, capsule_index)]
                    self.assertAlmostEqual(
                        distance2, first["distance_squared"], delta=2.0 ** -42)
                    second_hit = distance2 <= radius * radius
                    self.assertEqual(second_hit, first["hit"])
                    hit = hit or second_hit
                    checked += 1
                second_bits.append(int(hit))
            self.assertEqual(
                tuple(second_bits),
                tuple(fixture["canonical_oracle"]["per_query_hit"]))
        self.assertEqual(checked, 21)


if __name__ == "__main__":
    unittest.main()
