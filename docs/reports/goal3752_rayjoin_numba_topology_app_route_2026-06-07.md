# Goal3752 RayJoin Numba Topology App Route

## Purpose

Goal3749 added the reusable Numba side-aware topology helper. Goal3752 makes it
usable from the RayJoin benchmark app itself, so a learner or benchmark user can
run a real app-facing route rather than only reading the primitive/helper test.

The route is:

`v2_9_numba_side_aware_topology_reference`

## What It Does

The route loads real RayJoin CDB chain topology rows, builds explicit
caller-owned owner-face/side policy columns, runs the Python column reference,
then runs the no-RawKernel Numba CUDA continuation:

`filter_closed_shape_membership_candidate_columns_by_owner_face_side_numba`

The app reports:

- input topology row count,
- candidate count,
- Python reference row count,
- Numba row count,
- parity between Python column semantics and Numba CUDA semantics,
- phase timings,
- partner metadata and claim boundaries.

## A5000 Fixture Execution

Artifact:
`docs/reports/goal3752_rayjoin_numba_topology_app_route_a5000.json`

Command:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --workload overlay_seed --execution-route v2_9_numba_side_aware_topology_reference --no-rows
```

Result:

| Field | Value |
| --- | --- |
| Dataset | `tests/fixtures/rayjoin/br_county_subset.cdb` |
| Candidate rows | 3 |
| Numba rows | 3 |
| Python-column parity | `true` |
| Raw CUDA kernel required | `false` |
| Native engine app logic added | `false` |

This fixture run is correctness and usability evidence. It is not performance
evidence because the bundled fixture exposes only three topology rows and the
first call includes Numba JIT compilation cost.

## Why This Matters

This closes an important usability gap. Goal3749 proved the generic helper and
measured it on A5000. Goal3752 exposes it through the benchmark app so users can
see how to write explicit app-owned topology policy with RTDL + Python + Numba,
without CuPy RawKernel and without adding app-specific native engine logic.

## Boundary

Goal3752 does not authorize release action, public speedup wording, broad
RT-core claims, whole-RayJoin app speedup wording, RayJoin paper reproduction
wording, RTDL-beats-RayJoin wording, hidden partner selection, true-zero-copy
claims, or app-specific native-engine logic.

The promoted RayJoin performance route remains primitive-first RTDL/OptiX.
This route is a user-facing Numba reference for app-owned topology
continuation.
