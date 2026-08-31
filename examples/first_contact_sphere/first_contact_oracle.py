"""Independent oracle for the Goal5833 First Contact example.

This file imports no RTDL module.  Its numerical contract is explicit:

* every public input is first projected to finite IEEE-754 binary32, exactly
  as the public RTDL path does;
* the segment direction is rounded to binary32 after subtraction;
* ray/sphere discriminant signs are decided exactly over those binary32
  values (represented as rational numbers), so cancellation cannot turn a
  miss into a tangent; and
* roots stay symbolic: exact comparisons locate the entry root in ``[0,1]``
  and round it to nearest-even binary32 without evaluating a cancellation-
  prone quadratic formula.

This is an exact-classification policy, not an epsilon/margin heuristic.  An
exact zero discriminant is therefore a real tangent in the projected input
domain.  Candidate order is the frozen
``(ordered-f32(t), application_id)`` order.  Primitive index is retained only
as physical provenance: application IDs are unique, so it cannot decide a
legal semantic tie.
"""

from __future__ import annotations

import math
from fractions import Fraction
import struct
from typing import Sequence


U32_MAX = 0xFFFFFFFF
NUMERIC_POLICY = "binary32_projection__exact_symbolic_root__nearest_even_f32_v2"


def f32(value: float) -> float:
    try:
        projected = struct.unpack("<f", struct.pack("<f", float(value)))[0]
    except (OverflowError, TypeError, ValueError, struct.error) as exc:
        raise ValueError("finite binary32 value required") from exc
    if not math.isfinite(projected):
        raise ValueError("finite binary32 value required")
    return projected


def f32_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", f32(value)))[0]


def ordered_f32(value: float) -> int:
    bits = f32_bits(value)
    return (~bits & U32_MAX) if bits & 0x80000000 else bits ^ 0x80000000


def _exact(value: float) -> Fraction:
    """Return the exact rational value of an already-projected binary32."""

    return Fraction.from_float(value)


def _compare_value_to_root(
    value: Fraction,
    a: Fraction,
    half_b: Fraction,
    discriminant: Fraction,
    branch: int,
) -> int:
    """Compare rational ``value`` with one symbolic quadratic root.

    ``branch`` is ``-1`` for the entry root, ``0`` for an exact tangent, and
    ``+1`` for the exit root.  The result is negative/equal/positive when the
    value is below/equal/above that root.  Squaring is used only after the sign
    of ``a*value+half_b`` makes it equivalence-preserving.
    """

    y = a * value + half_b
    if branch == 0:
        delta = a * value + half_b
        return (delta > 0) - (delta < 0)
    if branch == -1:
        if y >= 0:
            return 1
        delta = discriminant - y * y
        return (delta > 0) - (delta < 0)
    if branch == 1:
        if y <= 0:
            return -1
        delta = y * y - discriminant
        return (delta > 0) - (delta < 0)
    raise ValueError("quadratic root branch must be -1, 0, or 1")


def _float_from_bits(bits: int) -> float:
    return struct.unpack("<f", struct.pack("<I", bits))[0]


def _round_symbolic_unit_root_to_f32(
    a: Fraction, half_b: Fraction, discriminant: Fraction, branch: int,
) -> float:
    """Correctly round a known root in ``[0,1]`` to binary32 nearest-even."""

    low_bits, high_bits = 0, f32_bits(1.0)
    while low_bits < high_bits:
        middle = (low_bits + high_bits + 1) // 2
        value = Fraction.from_float(_float_from_bits(middle))
        if _compare_value_to_root(
                value, a, half_b, discriminant, branch) <= 0:
            low_bits = middle
        else:
            high_bits = middle - 1
    lower = Fraction.from_float(_float_from_bits(low_bits))
    if _compare_value_to_root(
            lower, a, half_b, discriminant, branch) == 0:
        return _float_from_bits(low_bits)
    upper_bits = low_bits + 1
    upper = Fraction.from_float(_float_from_bits(upper_bits))
    midpoint = (lower + upper) / 2
    midpoint_order = _compare_value_to_root(
        midpoint, a, half_b, discriminant, branch)
    if midpoint_order < 0:
        return _float_from_bits(upper_bits)
    if midpoint_order > 0:
        return _float_from_bits(low_bits)
    # IEEE-754 ties-to-even: adjacent positive finite binary32 encodings
    # alternate least-significant significand parity.
    return _float_from_bits(low_bits if low_bits % 2 == 0 else upper_bits)


def first_contact(
    start: Sequence[float],
    end: Sequence[float],
    centers: Sequence[Sequence[float]],
    radii: Sequence[float],
    application_ids: Sequence[int],
) -> tuple[int, int, int]:
    if len(start) != 3 or len(end) != 3 or not centers \
            or len(centers) != len(radii) or len(centers) != len(application_ids):
        raise ValueError("closed First Contact input shape required")
    projected_start = tuple(f32(item) for item in start)
    projected_end = tuple(f32(item) for item in end)
    d = tuple(f32(projected_end[i] - projected_start[i]) for i in range(3))
    exact_d = tuple(_exact(item) for item in d)
    a = sum((item * item for item in exact_d), Fraction(0))
    if a == 0:
        raise ValueError("nonzero finite segment required")
    candidates = []
    for primitive, (center, radius, application_id) in enumerate(
            zip(centers, radii, application_ids)):
        if len(center) != 3:
            raise ValueError("finite vec3 center required")
        projected_center = tuple(f32(item) for item in center)
        r = f32(radius)
        if r <= 0.0:
            raise ValueError("positive finite radius required")
        if not isinstance(application_id, int) or isinstance(application_id, bool) \
                or not 0 <= application_id <= U32_MAX:
            raise ValueError("u32 application ID required")
        # Subtraction is represented exactly here.  The inputs themselves and
        # direction have already undergone the public path's binary32
        # projection; exact rational arithmetic is the oracle's deliberate
        # robust-classification policy.
        m = tuple(
            _exact(projected_start[i]) - _exact(projected_center[i])
            for i in range(3)
        )
        exact_r = _exact(r)
        c = sum((item * item for item in m), Fraction(0)) - exact_r * exact_r
        if c <= 0:
            raise ValueError("start must be strictly outside every sphere")
        half_b = sum((m[i] * exact_d[i] for i in range(3)), Fraction(0))
        discriminant = half_b * half_b - a * c
        if discriminant < 0:
            continue
        branches = (0,) if discriminant == 0 else (-1, 1)
        for branch in branches:
            if _compare_value_to_root(
                    Fraction(0), a, half_b, discriminant, branch) <= 0 \
                    and _compare_value_to_root(
                        Fraction(1), a, half_b, discriminant, branch) >= 0:
                t32 = _round_symbolic_unit_root_to_f32(
                    a, half_b, discriminant, branch)
                candidates.append((ordered_f32(t32), application_id, t32))
                break
    if not candidates:
        return 0, f32_bits(1.0), U32_MAX
    _, application_id, t = min(candidates)
    return 1, f32_bits(t), application_id


__all__ = [
    "NUMERIC_POLICY", "U32_MAX", "f32", "f32_bits", "first_contact",
    "ordered_f32",
]
