# Goal 573 External Review — RTXRMQ Closest-Hit Feature

Reviewer: Claude (claude-sonnet-4-6)
Date: 2026-04-18 (refreshed)
Artifacts reviewed:
- `docs/reports/goal573_rtxrmq_closest_hit_feature_2026-04-18.md`
- `scripts/goal573_rtxrmq_closest_hit_perf.py`
- `tests/test_goal573_rtxrmq_closest_hit.py`
- `docs/reports/goal573_rtxrmq_closest_hit_linux_2026-04-18.json`

---

## Verdict: ACCEPT

The missed RTXRMQ closest-hit feature is honestly and correctly solved for CPU
Python reference, `run_cpu`, and Embree. No false claims are made for
OptiX, Vulkan, or HIPRT.

---

## Geometry Encoding — Correctness

Element `i` with value `v` is encoded as two axis-aligned triangles in the
plane `x = v`, with YZ footprint `y ∈ [0, i+1]`, `z ∈ [i, n]`.

A query ray at `(oy = l+0.5, oz = r+0.5)` directed along `+X` hits element
`i` iff `l+0.5 < i+1` and `r+0.5 > i`, which simplifies to `l ≤ i ≤ r`.
This is exactly the RMQ membership predicate. Since `x = value` and the ray
travels in `+X`, the closest hit (minimum `t`) is the minimum value in
`[l, r]`. Decoding `triangle_id // 2` recovers the element index correctly.

Tie-break: smaller `t` (smaller value) wins; exact `t` tie breaks on smaller
`triangle_id` (smaller element index). This is deterministic and consistent
with "leftmost minimum" semantics.

The `tmax = 3.0` on query rays is safe: origin is `x = -1`, all triangles
are at `x ∈ [0, 1]`, so `t ∈ [1, 2]`.

---

## Test Coverage

Four unit tests exercise the full feature surface:

1. **Primitive smoke** — single ray, two triangles at `x=0.7` and `x=0.2`;
   confirms `triangle_id 11` (closer) is returned by
   `ray_triangle_closest_hit_cpu`.
2. **CPU reference RMQ parity** — 7-element hand-crafted array, three queries
   including single-element and multi-element ranges;
   `run_cpu_python_reference` matches `exact_rmq_cpu` oracle.
3. **`run_cpu` parity** — same case via the native CPU runtime surface,
   explicitly closing `run_cpu` support.
4. **Generated case** — 64 values, 24 queries, max range 10;
   `run_cpu_python_reference` matches oracle.

All 4 pass on both macOS (local) and Linux (`lx1`). The full 239-test suite
is clean on both platforms, confirming no regressions.

---

## Linux Performance Evidence

JSON is machine-generated (not hand-crafted). Key fields:

| Backend | `matches_exact_rmq` | Median (s) |
|---|:---:|---:|
| `cpu_python_reference` | `true` | `11.4085` |
| `embree` | `true` | `0.0274` |

Sample rows are byte-for-byte identical between both backends and
`expected_sample`, confirming correctness at scale (4096 values, 8192
triangles, 2048 query rays, max range 128). Embree ~416× faster than CPU
reference — plausible for BVH traversal replacing a pure-Python scan.

---

## Honesty Boundary

- Feature report: "It does not yet close OptiX, Vulkan, or HIPRT native
  closest-hit support."
- JSON `honesty_boundary` field repeats the same limitation verbatim.
- Performance script only iterates over `cpu_python_reference` and `embree`.
- Linux JSON records OptiX, Vulkan, and HIPRT as `FileNotFoundError`
  (libraries not built) — not silently skipped, not falsely claimed.

No overclaiming anywhere in the artifact set.

---

## Minor Observations (non-blocking)

- Script default `--values 2048` differs from the Linux run's 4096; both are
  valid. The JSON records the actual case used.
- Tests do not directly invoke Embree; Embree correctness is covered by the
  perf script. This is acceptable given the shared kernel path.
- `exact=False` in `ray_triangle_closest_hit(exact=False)` is intentional
  (floating-point conservatism flag, not a closest-hit toggle) and consistent
  with codebase convention.

---

## Conclusion

The implementation is correct, well-tested, and scoped exactly to what is
claimed. CPU Python reference, `run_cpu`, and Embree are verified against an
independent oracle. OptiX, Vulkan, and HIPRT are correctly deferred with no
false claims. This is an acceptable first closure of the missed RTXRMQ
closest-hit primitive.

**ACCEPT**
