"""Stdlib-only active-set oracle for the bounded Goal5835 mapping.

The algorithm is intentionally different from Goal5834-B1's closest-segment
implementation. It enumerates the interior and four boundary active sets of
the convex two-parameter distance quadratic.
"""

from __future__ import annotations


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _distance2_at(p, u, q, v, s, t):
    delta = tuple(p[i] + s * u[i] - q[i] - t * v[i] for i in range(3))
    return _dot(delta, delta)


def segment_segment_distance2(first_start, first_end, second_start, second_end):
    p, q = tuple(first_start), tuple(second_start)
    u = _sub(tuple(first_end), p)
    v = _sub(tuple(second_end), q)
    w = _sub(p, q)
    a, b, c = _dot(u, u), _dot(u, v), _dot(v, v)
    d, e = _dot(u, w), _dot(v, w)
    if a <= 0.0 or c <= 0.0:
        raise ValueError("nonzero edge and capsule segments required")
    clamp = lambda value: max(0.0, min(1.0, value))
    candidates = [
        (0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0),
        (0.0, clamp(e / c)), (1.0, clamp((e + b) / c)),
        (clamp(-d / a), 0.0), (clamp((b - d) / a), 1.0),
    ]
    determinant = a * c - b * b
    if determinant > 0.0:
        s = (b * e - c * d) / determinant
        t = (a * e - b * d) / determinant
        if 0.0 <= s <= 1.0 and 0.0 <= t <= 1.0:
            candidates.append((s, t))
    return min(_distance2_at(p, u, q, v, s, t) for s, t in candidates)


def edge_capsule_bits(capsules, edges):
    bits = []
    for edge_start, edge_end in edges:
        hit = any(segment_segment_distance2(
            edge_start, edge_end, capsule_start, capsule_end) <= radius * radius
            for capsule_start, capsule_end, radius, _identity in capsules)
        bits.append(int(hit))
    return tuple(bits), int(any(bits))


__all__ = ["edge_capsule_bits", "segment_segment_distance2"]
