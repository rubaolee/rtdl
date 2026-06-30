# Goal3750 Numba Reference Adequacy Closure After Goal3749

## Purpose

Goal3750 refreshes the v2.9 benchmark adequacy matrix after Goal3749 closed the
remaining `spatial_rayjoin` Numba-reference pressure point.

The user requirement is practical: if a benchmark app needs custom GPU logic,
RTDL should provide a high-performance Numba reference so users are not forced
to write CuPy RawKernel or raw CUDA code. Goal3742/3744 covered RT-DBSCAN,
Goal3746 covered Barnes-Hut exact-force continuation, and Goal3749 now covers
RayJoin side-aware topology continuation with a no-RawKernel reference.

## Current Result

No promoted benchmark app remains flagged as needing a Numba reference.

| App | Previous Numba status | Current status |
| --- | --- | --- |
| `rt_dbscan` | Needed component-continuation reference | Covered by Goal3742/3744 |
| `barnes_hut` | Needed force-vector continuation reference | Covered by Goal3746 |
| `spatial_rayjoin` | Needed closed-shape/topology continuation reference | Covered by Goal3749 |

## Goal3749 RayJoin Evidence

Goal3749 adds
`filter_closed_shape_membership_candidate_columns_by_owner_face_side_numba`, a
generic no-RawKernel Numba CUDA helper for the side-aware owner-face membership
filter. The helper preserves the existing columnar semantics and supports both
public ids and prepared ordinals.

A5000 same-contract artifact:
`docs/reports/goal3749_rayjoin_side_aware_topology_numba_a5000/summary.json`

| Candidate rows | CuPy best s | Numba best s | Numba/CuPy |
| ---: | ---: | ---: | ---: |
| 16,384 | 0.066093 | 0.006677 | 9.899x |
| 65,536 | 0.112891 | 0.010790 | 10.462x |
| 262,144 | 0.228969 | 0.013859 | 16.521x |
| 1,048,576 | 0.441605 | 0.024823 | 17.790x |

All timing rows preserve keep-count parity. The timing is same-contract partner
continuation evidence, not whole-RayJoin app evidence.

## Updated Matrix Meaning

The active adequacy matrix in `src/rtdsl/v2_9_benchmark_adequacy.py` now records
`rtdl.v2_9.benchmark_adequacy_after_goal3749.v1`.

- `numba_reference_needed_apps` is empty.
- `spatial_rayjoin` remains `strong`, with the explicit boundary that Goal3749
  is not RayJoin paper reproduction and not an RTDL-beats-RayJoin claim.
- RT-DBSCAN, Barnes-Hut, and RayJoin now all have user-facing Numba references
  for their custom continuation paths.

## Boundary

Goal3750 does not authorize release action, public speedup wording, whole-app
speedup wording, broad RT-core claims, RayJoin paper reproduction wording,
RTDL-beats-RayJoin wording, hidden partner selection, true-zero-copy claims, or
app-specific native-engine logic.

The next major engineering direction is no longer "add missing Numba
references"; it is larger performance work: whole-benchmark packet refreshes,
HIPRT/AMD primitive parity, and deeper generic primitives where the benchmark
apps still expose real runtime gaps.
