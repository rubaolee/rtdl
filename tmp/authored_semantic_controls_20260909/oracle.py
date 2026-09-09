"""Predeclared geometric cases and scalar expected output; imports no RTDL."""
from __future__ import annotations

U32_MAX = 0xFFFFFFFF
HIT_TAG = 0xA11CE001
MISS_TAG = 0xA11CE000


def input_arrays():
    import numpy as np
    vertices, triangles, queries, selected = [], [], [], []
    for j in range(16):
        for z in (2.0, 1.0):
            first = len(vertices)
            vertices.extend(((4*j, 0, z), (4*j+2, 0, z), (4*j, 2, z)))
            triangles.append((first, first+1, first+2))
        queries.extend(((4*j+.5, .5, 0, 0, 0, 1, 4),
                        (4*j+.5, .5, 1.5, 0, 0, 1, 4),
                        (4*j+.5, .5, 0, 0, 0, 1, .5),
                        (4*j+2.5, 2.5, 0, 0, 0, 1, 4)))
        selected.extend((2*j+1, 2*j, None, None))
    return {
        "vertices": np.array(vertices, dtype="<f4"),
        "triangles": np.array(triangles, dtype="<u4"),
        "first_values": np.array([1000+11*p for p in range(32)], dtype="<u4"),
        "second_values": np.array([31+3*p for p in range(32)], dtype="<u4"),
        "queries": np.array(queries, dtype="<f4"),
    }, selected


def expected_rows(power, binding, *, reversed_order=False):
    """P2=F+2B and P3=F+3B; swapping makes B+kF. No GPU data enters."""
    import numpy as np
    if power not in (2, 3) or binding not in ("normal", "swapped"):
        raise ValueError("unregistered source/binding cell")
    _, selected = input_arrays()
    result = []
    for p in selected:
        if p is None:
            result.append((U32_MAX, 0, MISS_TAG))
        else:
            f, b = 1000+11*p, 31+3*p
            value = f+power*b if binding == "normal" else b+power*f
            result.append((value, 1, HIT_TAG))
    if reversed_order:
        result.reverse()
    return np.array(result, dtype="<u4")


def independently_check_geometry():
    """Scalar ray-plane / barycentric verification of the predeclared cases."""
    arrays, selected = input_arrays()
    observed = []
    for q in arrays["queries"]:
        ox, oy, oz, dx, dy, dz, tmax = map(float, q)
        assert (dx, dy, dz) == (0., 0., 1.)
        hits = []
        for p, tri in enumerate(arrays["triangles"]):
            a, b, c = (tuple(map(float, arrays["vertices"][int(k)])) for k in tri)
            t = a[2] - oz
            u, v = (ox-a[0])/(b[0]-a[0]), (oy-a[1])/(c[1]-a[1])
            if 0 <= t <= tmax and u >= 0 and v >= 0 and u+v <= 1:
                assert u > 0 and v > 0 and u+v < 1
                hits.append((t, p))
        hits.sort()
        assert len(hits) < 2 or hits[0][0] != hits[1][0]
        observed.append(None if not hits else hits[0][1])
    if observed != selected:
        raise AssertionError("predeclared geometry disagrees with scalar intersection")
    return {"rays": 64, "triangles": 32, "hit_rows": 32, "miss_rows": 32,
            "strict_interior": True, "no_equal_distance_candidates": True}
