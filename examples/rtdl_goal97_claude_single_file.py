from __future__ import annotations

import sys
from collections import Counter

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def _lsi_rank_kernel():
    probes = rt.input("probes", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    builds = rt.input("builds", rt.Segments, layout=rt.Segment2DLayout, role="build")
    hits = rt.refine(
        rt.traverse(probes, builds, accel="bvh"),
        predicate=rt.segment_intersection(exact=False),
    )
    return rt.emit(hits, fields=["left_id", "right_id"])


def _build_inputs(values: list[int]) -> dict[str, tuple]:
    if any(v < 0 for v in values):
        raise ValueError("nonnegative integers only")
    far = float(max(values, default=0) + 1)
    probes = tuple(
        rt.Segment(id=i, x0=0.0, y0=v + 0.5, x1=far, y1=v + 0.5)
        for i, v in enumerate(values)
    )
    builds = tuple(
        rt.Segment(id=i, x0=float(v), y0=0.0, x1=float(v), y1=float(v + 1))
        for i, v in enumerate(values)
    )
    return {"probes": probes, "builds": builds}


def _counts_from_rows(rows: tuple[dict, ...], n: int) -> list[int]:
    c = Counter(int(r["left_id"]) for r in rows)
    return [c[i] for i in range(n)]


def solve(values: list[int], backend: str = "cpu_python_reference") -> dict:
    inputs = _build_inputs(values)
    dispatch = {
        "cpu_python_reference": rt.run_cpu_python_reference,
        "cpu":                  rt.run_cpu,
        "embree":               rt.run_embree,
        "optix":                rt.run_optix,
        "vulkan":               rt.run_vulkan,
    }
    if backend not in dispatch:
        raise ValueError(f"unknown backend: {backend!r}")
    rows = dispatch[backend](_lsi_rank_kernel, **inputs)
    counts = _counts_from_rows(rows, len(values))
    paired = list(zip(values, counts, range(len(values))))
    asc  = [v for v, _, _ in sorted(paired, key=lambda t: (-t[1], t[2]))]
    desc = [v for v, _, _ in sorted(paired, key=lambda t: ( t[1], t[2]))]
    assert asc  == sorted(values),               "ascending mismatch"
    assert desc == sorted(values, reverse=True), "descending mismatch"
    return {"values": values, "hit_counts": counts, "ascending": asc, "descending": desc}


if __name__ == "__main__":
    vals   = list(map(int, sys.argv[1:])) if len(sys.argv) > 1 else [3, 1, 4, 1, 5, 0, 2, 5]
    result = solve(vals)
    print(f"input     : {result['values']}")
    print(f"hit_counts: {result['hit_counts']}")
    print(f"ascending : {result['ascending']}")
    print(f"descending: {result['descending']}")
    print("ok")
