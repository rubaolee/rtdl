# Spatial RayJoin Code Walkthrough

Status: current v2.10 source-tree benchmark-app explanation.

This document explains
`rtdl_rayjoin_v2_spatial_join_app.py` for two audiences:

- new RTDL learners who want to understand how spatial join operations are
  expressed in Python+RTDL+partners;
- RayJoin authors or spatial-system researchers who want to understand what is
  new in RTDL at the language level, optimization level, and performance level.

It is not a claim that RTDL fully reproduces the RayJoin paper system.

## One-Sentence Summary

The app decomposes RayJoin-style work into generic RTDL spatial primitives plus
Python-owned interpretation:

```text
load CDB-style records -> build generic point/segment/shape inputs
-> choose PIP, LSI, or overlay-seed contract
-> run CPU, Embree, OptiX, or partner continuation route
-> compare with CPU oracle and emit claim-boundary metadata
```

## Workloads

| Workload | Spatial operation | Output contract | Who owns the app meaning |
| --- | --- | --- | --- |
| `pip` | point-in-polygon positive assignment | `point_to_polygon_positive_hit_rows` or scalar count | Python maps positive hits to RayJoin-style point/polygon assignments. |
| `lsi` | line-segment intersection | `segment_segment_intersection_rows`, compact grouped count, or dense left-id count | Python maps generic segment pairs to left/right relation semantics. |
| `overlay_seed` | polygon-pair dependency seed discovery | `overlay_pair_dependency` rows or active pair count | Python owns overlay policy and full overlay continuation. |

The native engine does not export a RayJoin-specific ABI. It sees generic
primitive families such as point/closed-shape membership, segment-pair
intersection, grouped count, shape-pair relation flags, and typed candidate
columns.

## File Map

| Code area | Purpose |
| --- | --- |
| dataset loading helpers | Resolve checked-in fixtures or external `.cdb` paths and build workload-specific inputs. |
| reference helpers | Produce CPU Python oracle rows and summaries for PIP, LSI, and overlay seed workloads. |
| generic backend runner | Run the portable RTDL kernel path through CPU, Embree, or OptiX when available. |
| prepared OptiX routes | Reuse static geometry through prepared OptiX handles and run prepared traversal/count contracts. |
| prepared handle classes | Expose reusable Python handles for repeated PIP, LSI, and overlay queries. |
| partner continuation routes | Use CuPy or Numba only where the app explicitly chooses continuation or baseline work. |
| CLI and JSON payload builder | Make backend, route, result mode, parity, timing, and claim boundary visible. |

## The Learner Path Through The Code

Start with the CPU oracle:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --backend cpu_python_reference --no-rows
```

That route exercises:

```text
run_rayjoin_suite(...)
  -> run_rayjoin_workload(...)
     -> _load_rayjoin_case(...)
     -> _run_backend(...)
     -> _summarize_rows(...)
```

The important output fields are:

| Field | Meaning |
| --- | --- |
| `all_match_cpu_python_reference` | Suite-level correctness signal for the checked workload set. |
| `parity_vs_cpu_python_reference` | Per-workload correctness signal. |
| `summary.output_contract` | The generic result shape returned by the route. |
| `native_engine_boundary` | Reminder that app policy stays outside the native engine. |
| `claim_boundary` | What the run does not authorize. |

After that, inspect one workload at a time:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --workload pip --backend cpu_python_reference --no-rows
PYTHONPATH=src:. python examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --workload lsi --backend cpu_python_reference --no-rows
PYTHONPATH=src:. python examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --workload overlay_seed --backend cpu_python_reference --no-rows
```

This is the correct order for a learner: understand the contract and oracle
before reading CUDA, OptiX, or partner continuation code.

## Language-Level Difference From RayJoin

RayJoin is a specialized spatial join system. RTDL is a language/runtime surface
that tries to expose the reusable parts as generic contracts.

| RayJoin-style implementation concern | RTDL language/runtime expression |
| --- | --- |
| Specialized PIP, LSI, and overlay kernels | Generic point/closed-shape, segment-pair, shape-pair, count, and row-stream primitives. |
| Paper-specific dataset and workload policy | Python loader and benchmark app policy. |
| Application-specific output interpretation | Python summaries and optional partner continuation. |
| Per-workload optimized routes | Explicit route choice recorded in JSON metadata. |
| Whole-system paper result | Contract-specific evidence with claim boundaries. |

The key RTDL design point is that a future user should not need a new native
engine for every spatial application. They should find or compose generic
spatial primitives, then keep app-specific policy in Python or the selected
partner.

## Optimization-Level Difference From RayJoin

RTDL does not copy RayJoin's implementation one-for-one. It uses the RayJoin
workloads to pressure-test generic primitives.

| Optimization idea | RTDL version in this app | Why it matters |
| --- | --- | --- |
| Prepared static geometry | Prepared OptiX handles for right-side point, segment, or shape sets. | Avoids rebuilding static acceleration data for repeated queries. |
| Packed left input reuse | `pack_*_left_*` helpers and `run_packed_left(...)` methods. | Avoids paying Python packing cost for the same left batch repeatedly. |
| Scalar count path | `--result-mode count`, dense left-id count, and active pair count routes. | Avoids materializing witness rows when the app only needs a count. |
| Compact grouped count | Generic compact `group_key[]` plus `count[]` device columns. | Keeps grouped summaries generic and avoids RayJoin-specific native output. |
| Shape-pair active count | Prepared shape-pair relation flags plus device-side active count continuation. | Keeps overlay seed count fast while full overlay interpretation stays app-level. |
| CuPy dense baselines | Dense CUDA-core PIP and overlay baselines. | Provides a strong non-RT opponent so RTDL does not overclaim. |
| Numba reference continuation | Python-source no-RawKernel continuation for selected custom logic. | Lets users write custom GPU logic in Python syntax when raw CUDA kernels are not desired. |

The optimization lesson is not "always use OptiX". The lesson is:

```text
Use RTDL/OptiX when traversal and prepared geometry dominate.
Use a partner when dense CUDA-core array work is the better contract.
Keep the route visible and measured.
```

## Main Execution Routes

| Route | Workload | Role |
| --- | --- | --- |
| default backend route | `pip`, `lsi`, `overlay_seed` | Correctness and backend parity through CPU, Embree, or OptiX. |
| `prepared_optix` | all three workloads | Prepared traversal/count route with phase telemetry. |
| `prepared_optix_cupy_refined_pip` | `pip` | Generic OptiX candidate columns plus prepared CuPy exact ring refiner. |
| `prepared_optix_compact_grouped_count` | `lsi` | Generic segment-pair candidate columns plus compact grouped count. |
| `prepared_optix_left_id_dense_count` | `lsi` | Generic fused dense left-id count when witness IDs are unnecessary. |
| `prepared_optix_shape_pair_active_count` | `overlay_seed` | Generic prepared shape-pair active count. |
| segmented compact-mask Numba plan/preview | all workloads | User-selected Numba continuation reference, not the promoted OptiX route. |
| side-aware topology Numba reference | `overlay_seed` | App-owned topology policy reference, not native engine semantics. |

## How The Prepared Handles Work

The prepared-handle classes are the best place to see the v2.10 programming
style.

For repeated LSI count queries:

```python
from examples.current.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (
    pack_rayjoin_optix_compact_grouped_count_left_segments,
    prepare_rayjoin_optix_compact_grouped_count_segments,
)

with prepare_rayjoin_optix_compact_grouped_count_segments(right_segments) as prepared:
    packed_left = pack_rayjoin_optix_compact_grouped_count_left_segments(left_segments)
    payload = prepared.run_packed_left_dense_count(packed_left, include_rows=False)

print(payload["summary"])
```

What is generic:

- the right-side prepared segment scene;
- the left segment input columns;
- the segment-pair count or grouped-count primitive;
- the typed count columns.

What is app-owned:

- which CDB records are left or right;
- how left IDs are remapped;
- whether the caller wants dense counts, compact counts, or witness rows;
- how the count is reported as a RayJoin-style result.

For repeated overlay active-count queries:

```python
from examples.current.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (
    pack_rayjoin_optix_shape_pair_active_count_left_shapes,
    prepare_rayjoin_optix_shape_pair_active_count,
)

with prepare_rayjoin_optix_shape_pair_active_count(right_shapes) as prepared:
    packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_shapes)
    payload = prepared.run_packed_left(packed_left)

print(payload["summary"])
```

Again, the primitive remains generic. Full overlay construction is outside this
count-oriented benchmark route.

## Performance-Level Reading

Read performance as contract-specific evidence:

| Contract family | Current lesson |
| --- | --- |
| Scoped all-backend spatial join summary | The current application catalog records Embree `0.0203149s`, OptiX `0.000529638s`, about `38.4x` for the scoped standard row. |
| LSI and overlay scalar answers on bounded public CDB slices | Current partner guidance records RTDL/OptiX at about `260x` faster than dense partner baselines for the scalar-answer contracts. |
| PIP one-shot bounded public CDB scalar count | CuPy dense CUDA-core count is still the faster current route at that size. |
| Resident repeated PIP | The prepared batch executor is the current RTDL/OptiX direction, with partner guidance recording about `0.024ms/request` for batch 100. |

Those numbers are not a universal RayJoin speedup claim. They say which
contract currently favors which route.

The user-facing rule is:

```text
Do not publish "RTDL beats RayJoin" from this app.
Publish: workload, dataset, route, partner, hardware, contract, correctness,
and timing.
```

## What Is New For RayJoin Authors

At the language level:

- RTDL turns PIP, LSI, and overlay seed logic into reusable primitive contracts
  rather than app-specific native exports.
- The app can still name RayJoin concepts, but the engine does not.
- Route choice is explicit and recorded rather than hidden behind a dispatcher.

At the optimization level:

- RTDL exposes prepared right-side geometry and packed left-side inputs as
  reusable Python handles.
- Scalar-answer routes avoid witness row materialization when the app only
  needs counts.
- Generic grouped-count and active-count continuations let different spatial
  apps reuse the same runtime pieces.
- CuPy and Numba are competitors or continuations chosen by the user, not
  privileged hidden layers.

At the performance level:

- RTDL/OptiX is strong when prepared traversal/count work dominates, especially
  LSI and overlay-style scalar contracts on the measured public-CDB slices.
- Dense CUDA-core partner code can still win simple PIP count rows.
- The benchmark is therefore useful as a route-selection study and generic
  primitive design pressure, not as a full paper reproduction claim.

## Current Limits

- Full RayJoin paper reproduction is not claimed.
- Full polygon overlay construction is not the promoted contract here.
- PIP route choice remains dataset and result-contract dependent.
- Native code remains app-agnostic; RayJoin-specific topology and dataset policy
  stay in Python or partner code.
- Performance claims require reviewed artifacts with command, commit, hardware,
  dataset, partner, backend, correctness, and timing.

## Related Files

- [Spatial / RayJoin-Style Study](README.md)
- [RayJoin Dataset And Reproduction Notes](../../../../docs/research/rayjoin/README.md)
- [Benchmark Partner Reference Matrix](../../../../docs/learn/benchmark_partner_reference_matrix.md)
- [Application Catalog](../../../../docs/application_catalog.md)
