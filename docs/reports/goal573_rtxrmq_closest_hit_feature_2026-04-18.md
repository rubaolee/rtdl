# Goal 573: RTXRMQ Closest-Hit Feature Closure

Date: 2026-04-18

## Verdict

ACCEPT as the first implementation of the missed RTXRMQ feature.

RTDL now has a public `ray_triangle_closest_hit` predicate and an exact bounded
RTXRMQ-style RMQ workload using that primitive. The feature is implemented for
CPU Python reference and Embree. OptiX, Vulkan, and HIPRT remain future native
backend work for this specific primitive.

## What Changed

- Added `rt.ray_triangle_closest_hit(exact=False)`.
- Added `rt.ray_triangle_closest_hit_cpu(...)`.
- Added `run_cpu(...)` support through the native CPU/oracle runtime surface.
- Added Embree native 3D closest-hit ABI:
  `rtdl_embree_run_ray_closest_hit_3d`.
- Added exact RTXRMQ-style workload script:
  `/Users/rl2025/rtdl_python_only/scripts/goal573_rtxrmq_closest_hit_perf.py`.
- Added tests:
  `/Users/rl2025/rtdl_python_only/tests/test_goal573_rtxrmq_closest_hit.py`.
- Updated public docs to mention the new exact bounded RTXRMQ gate and backend
  boundary.

## Semantics

The new predicate returns one row per ray that hits at least one triangle:

```python
hits = rt.refine(candidates, predicate=rt.ray_triangle_closest_hit(exact=False))
return rt.emit(hits, fields=["ray_id", "triangle_id", "t"])
```

Tie behavior:

- smaller `t` wins
- if `t` ties exactly, smaller `triangle_id` wins
- miss rays emit no row

## Exact RMQ Encoding

The exact bounded RMQ app maps:

- each array element to two triangles forming a rectangle in query-coordinate
  space
- triangle X coordinate to the element value
- query `(l,r)` to a ray from `x=-1` along `+X` at `(y=l+0.5, z=r+0.5)`

The ray intersects element `i` iff `l <= i <= r`. Because X is the element
value, the closest hit is the minimum value in the query range. The returned
triangle id is decoded back to the element index with `triangle_id // 2`.

## Test Evidence

Local focused test:

```text
python3 -m unittest tests.test_goal573_rtxrmq_closest_hit
Ran 4 tests in 0.013s
OK
```

Local full discovery:

```text
python3 -m unittest discover -s tests
Ran 239 tests in 61.701s
OK
```

Linux focused test:

```text
python3 -m unittest tests.test_goal573_rtxrmq_closest_hit
Ran 4 tests in 0.012s
OK
```

Linux full discovery:

```text
python3 -m unittest discover -s tests
Ran 239 tests in 144.697s
OK
```

## Linux Performance

Linux JSON:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal573_rtxrmq_closest_hit_linux_2026-04-18.json`

Host:

- `lx1`
- `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- Python `3.12.3`
- GPU present: `NVIDIA GeForce GTX 1070, 580.126.09`
- Embree `4.3.0`

Case:

- values: `4096`
- triangles: `8192`
- query rays: `2048`
- max query range: `128`
- iterations: `3`

| Backend | Median seconds | Exact RMQ parity |
|---|---:|---|
| CPU Python reference | `11.408521` | yes |
| Embree | `0.027440` | yes |

Derived speedup:

- Embree vs CPU Python reference: about `416x`.

## Boundary

This closes the missing language/runtime primitive for CPU reference and Embree.
It does not yet close OptiX, Vulkan, or HIPRT native closest-hit support. Those
backends must not be claimed for exact RTXRMQ until their closest-hit kernels
are implemented and tested.

## Consensus

- Claude review: `/Users/rl2025/rtdl_python_only/docs/reports/goal573_external_review_2026-04-18.md`
- Gemini Flash review: `/Users/rl2025/rtdl_python_only/docs/reports/goal573_gemini_flash_review_2026-04-18.md`

Both final reviews returned `ACCEPT`.
