# Goal691: DB Prepared/Native Aggregate And Segment/Polygon OptiX Action Review

Date: 2026-04-21

Prior work:
- `docs/reports/goal689_optix_app_performance_review_2026-04-21.md`
- `docs/reports/goal690_gemini_optix_consensus_action_plan_2026-04-21.md`

Scope: concrete action plan for two specific work threads identified by goal689
and confirmed by goal690:

1. DB analytics — prepared/native aggregate optimization.
2. Segment/polygon apps — OptiX host-indexed remediation.

Both threads require an explicit separation between correctness support and
RT-core performance claims. That separation is stated up front and carried
through every action item.

---

## Correctness Support vs RT-Core Performance Claims

These are distinct properties. Every action item below is annotated with which
property it advances.

**Correctness support** means the app produces verifiably correct results.
Host-indexed fallback paths, CPU refinement, and Python reductions can all
provide correctness support. Correctness support is a necessary condition for
any performance claim but is not itself a performance claim.

**RT-core performance claim** means the dominant runtime cost of the operation
runs as native OptiX ray traversal on RTX-class hardware and the result is
measured against a CPU or CUDA-compute baseline on the same hardware. No
RT-core performance claim is valid unless:

- the dominant operation is OptiX traversal (not host-indexed, not pure CUDA
  compute, not Python post-processing);
- the measurement is taken on RTX-class NVIDIA hardware (GTX 1070 does not
  have RT cores and cannot validate this claim);
- phase-split timing is available, separating at minimum: Python construction,
  RTDL packing, native prepare, native execute, copy-back, row materialization,
  and app post-process.

The current DB analytics and segment/polygon OptiX app paths have correctness
support. Neither currently has a validated RT-core performance claim. The action
plans below work toward earning the RT-core claim, without making it prematurely.

---

## Thread 1: DB Analytics — Prepared/Native Aggregate Optimization

### Current State

`examples/rtdl_database_analytics_app.py` wraps two sub-apps
(`rtdl_v0_7_db_app_demo` and `rtdl_sales_risk_screening`) and exposes
`--backend optix`. The app's own `data_flow` field documents the current shape:

```
application-owned denormalized rows
→ bounded RTDL DB kernels
→ scan and grouped aggregate rows
→ Python-owned dashboard or risk-summary JSON
```

Real OptiX BVH candidate discovery is present in this path. However, goal689
identified four bottleneck layers that prevent this from being an OptiX
performance app today:

| Bottleneck layer | Current behavior |
| --- | --- |
| Python input construction | Application-owned rows built in Python before any RTDL call |
| RTDL packing/ctypes | Python-to-native encoding cost; goal689 notes this can dominate small-scale "prepare" time |
| Candidate copy-back | BVH candidate results copied back to host before CPU exact filtering |
| CPU exact filtering and grouping | Aggregate/grouped outputs computed on CPU from candidate rows |
| Dict-row materialization | Results returned as `tuple[dict, ...]`; full Python dict allocation per row |
| Python dashboard/JSON reduction | `Python-owned dashboard or risk-summary JSON` — app-level reduction is Python |

**Current performance classification: `python_interface_dominated`** (real OptiX
BVH traversal present for candidate discovery; app performance dominated by
Python/ctypes and CPU post-processing layers).

### Action Plan

**Step DB-1 (Correctness support, prerequisite).** Verify correctness parity
of the OptiX DB path against the `cpu_python_reference` path for both
`regional_dashboard` and `sales_risk` scenarios at small, medium, and large
scale. This is already implicit in the existing app structure but must be
explicitly gated before any prepared-dataset API is added, so that the gate
does not regress when the data layout changes.

**Step DB-2 (Performance: packing measurement).** Add a phase-split profiler
call around `rtdl_v0_7_db_app_demo.run_app(backend)` and
`rtdl_sales_risk_screening.run_case(backend)` that records wall time for:
Python input construction, RTDL packing, native prepare, native execute,
copy-back, row materialization, and Python post-process (JSON/dashboard). This
is required before any optimization claim can be verified or compared.

**Step DB-3 (Performance: prepared columnar dataset).** Introduce a
`prepare_db_dataset(rows, backend)` path that converts application-owned
denormalized rows into a native columnar representation (contiguous typed
arrays) once, reusable across multiple predicate queries. The goal is to remove
the per-query Python-to-ctypes encoding cost from the hot path. This step
advances performance but does not change correctness guarantees.

**Step DB-4 (Performance: native grouped outputs).** Introduce a
`run_grouped_aggregate(prepared_dataset, predicates, group_by, agg)` call that
returns grouped aggregate results as a compact native structure (e.g., numpy
arrays or a ctypes struct array) rather than `tuple[dict, ...]`. This removes
dict-row materialization and Python groupby from the critical path for
analytics queries.

**Step DB-5 (Performance: batched predicate execution).** Where the app
currently iterates multiple predicates sequentially, batch them into a single
native pass when the prepared dataset is resident on the device. This is
separate from the grouping work and may require API design before implementation.

**Step DB-6 (RT-core claim gate, RTX-class hardware).** After steps DB-3 and
DB-4 are in place, run phase-split benchmarks on RTX-class hardware. If native
execute time dominates and the dominant operation is OptiX BVH traversal (not
CUDA-compute or host-indexed), the DB analytics app can advance to an
`optix_traversal` classification. Until this measurement is available, the
classification remains `python_interface_dominated`.

### What DB Analytics Cannot Claim Now

- DB analytics with `--backend optix` is **not** an RT-core accelerated
  database query engine. It is an OptiX-backed spatial candidate discovery
  step followed by CPU and Python post-processing.
- Performance claims comparing DB OptiX to a CPU baseline must control for
  the full phase split, not just the native execute time.
- GTX 1070 results for DB OptiX are useful for CUDA/backend compatibility
  verification, not for RT-core or traversal-acceleration claims.

---

## Thread 2: Segment/Polygon Apps — OptiX Host-Indexed Remediation

### Current State

Three apps expose `--backend optix` for segment/polygon workloads:

| App | OptiX call | Row output |
| --- | --- | --- |
| `rtdl_road_hazard_screening.py` | `rt.run_optix(road_hazard_hitcount, ...)` | per-segment hit-count rows; Python list comprehension for `priority_segments` |
| `rtdl_segment_polygon_hitcount.py` | `rt.run_optix(segment_polygon_hitcount_reference, ...)` | per-pair hit-count rows |
| `rtdl_segment_polygon_anyhit_rows.py` | `rt.run_optix(segment_polygon_anyhit_rows_reference, ...)` | per-pair any-hit rows |

All three apps pass a reference kernel directly to `rt.run_optix()`. Goal689
and goal690 both identify the segment/polygon OptiX app path as defaulting to
host-indexed candidate reduction, not native OptiX traversal, unless a
separate native mode is explicitly enabled and gated. No native mode flag
is visible in the current app CLIs.

`rtdl_road_hazard_screening.py` defines its kernel with
`@rt.kernel(backend="rtdl", precision="float_approx")` and calls
`rt.traverse(roads, hazards, accel="bvh")`. On paper this is the OptiX
traversal kernel shape, but the actual dispatch path through `rt.run_optix()`
and the native library determines whether this becomes RT traversal or
host-indexed BVH candidate reduction. Goal689 classifies these as
`host_indexed_fallback` under the default dispatch.

**Current performance classification: `host_indexed_fallback`** (OptiX-facing
API; candidate reduction dispatches to CPU-side indexed logic under the current
default; correctness is valid, RT-core performance is not).

Additional risk for `rtdl_segment_polygon_anyhit_rows.py`: output volume grows
as the cross-product of intersecting segment/polygon pairs. If the app only
needs per-segment any-hit flags or counts, emitting all pair rows is the wrong
performance contract regardless of backend.

### Action Plan

**Step SP-1 (Correctness support, prerequisite).** Explicitly document and
test the correctness of the `--backend optix` path for all three apps against
the `cpu_python_reference` baseline. This must include:

- the authored minimal datasets currently used as defaults;
- the `br_county_subset` tiled datasets at x2, x4, x8 copies;
- an assertion that the OptiX path and the reference path agree on hit-count
  values and any-hit flags for every query in the test set.

This step does not change the host-indexed vs. native classification. It
establishes the correctness baseline required before any remediation work can
be validated.

**Step SP-2 (Transparency, no-code).** Add an explicit CLI note or `--info`
flag to each app that prints its current OptiX performance classification
(`host_indexed_fallback`) and a brief description of what that means. This is
consistent with the `rtdsl.optix_app_performance_matrix()` API added in goal690
and ensures users do not interpret `--backend optix` as RT-core acceleration.

**Step SP-3 (Remediation path A: native OptiX segment/polygon kernel).** If
the native library supports a true OptiX traversal path for segment/polygon
intersection (i.e., ray-cast segments against a polygon BVH using OptiX custom
primitives or triangle mesh approximation), wire it as a named mode in the
native dispatch and expose it behind `--optix-native` or equivalent. Gate this
path on:

- correctness parity with the reference on the test datasets from step SP-1;
- phase-split timing showing native execute dominates over Python/interface
  overhead at medium and large scale;
- at least one RTX-class hardware measurement.

Until all three gates pass, `--optix-native` must be an experimental flag, not
the default. The default continues to be the host-indexed path, which has
correctness support.

**Step SP-4 (Remediation path B: reclassification if native path is not
viable).** If a native OptiX traversal path for segment/polygon is not
achievable in the current library scope (e.g., the geometry cannot map cleanly
to OptiX primitives or the custom-primitive overhead exceeds the host-indexed
path), the apps should be reclassified in the machine-readable matrix:

- `optix_app_class` → `host_indexed_fallback` (already accurate; make it
  explicit in the matrix entry rather than implied).
- Add a `remediation_status` field: `reclassified_correctness_only`.
- Update the public app catalog accordingly.

This is not a regression. It is an honest statement of what the app provides.

**Step SP-5 (Output volume remediation for anyhit_rows).** Independent of
SP-3 and SP-4: add a `--count-only` or `--flags-only` mode to
`rtdl_segment_polygon_anyhit_rows.py` that returns per-segment any-hit flags
or counts as a compact native array rather than the full pair-row list. This
reduces output volume and Python materialization cost regardless of whether the
underlying backend is host-indexed or native OptiX. This step advances
performance independently of the traversal question.

**Step SP-6 (Road hazard hot-segment path).** `rtdl_road_hazard_screening.py`
already has the right output shape (per-segment hit-count, Python list
comprehension for `priority_segments`). Once the segment/polygon native mode
passes its correctness gate (SP-3) or the reclassification is accepted (SP-4),
the road hazard app should return `priority_segments` directly from a native
per-segment aggregate rather than via Python list comprehension over
`tuple[dict, ...]` rows.

### What Segment/Polygon Apps Cannot Claim Now

- None of the three segment/polygon apps with `--backend optix` are RT-core
  accelerated spatial intersection tools. They are correctness-valid apps that
  use the OptiX-facing API to dispatch what is currently a host-indexed
  candidate reduction.
- `--backend optix` in these apps does not mean RT-core traversal is used.
  It means the native library's OptiX host path was invoked, and that path
  currently resolves to CPU-side indexed logic.
- The float-approx precision flag on `road_hazard_hitcount` is a hint to the
  backend, not a guarantee that GPU approximate traversal is used.

---

## Cross-Cutting: Correctness/Performance Separation Enforcement

Both threads above require the same architectural enforcement point: every app
that exposes `--backend optix` must clearly separate what it guarantees
(correctness) from what it claims (performance acceleration category).

**Machine-readable classification (goal690 API).** The
`rtdsl.optix_app_performance_matrix()` and `rtdsl.optix_app_performance_support(app)`
APIs added in goal690 are the authoritative source for per-app classification.
All action steps above that change classification must update these APIs.

**Phase-split benchmark requirement.** No app-level performance comparison
between OptiX and CPU should be published without a phase-split table covering
at minimum: Python construction, RTDL packing, native prepare, native execute,
copy-back, row materialization, app post-process, and total wall time. A single
wall-time number is misleading when Python and interface costs dominate.

**RTX-class hardware requirement for RT-core claims.** No RT-core claim is
valid without measurement on RTX-class NVIDIA hardware. GTX 1070 results remain
valid for CUDA driver compatibility and backend portability. They are not
RT-core evidence.

---

## Prioritized Work Order

| Priority | Step | Property | Blocker |
| --- | --- | --- | --- |
| 1 | SP-1 | Correctness | None — run existing tests explicitly |
| 2 | DB-1 | Correctness | None — run existing tests explicitly |
| 3 | DB-2 | Performance measurement | DB-1 |
| 4 | SP-2 | Transparency | SP-1 |
| 5 | DB-3 | Performance | DB-2 (baseline needed) |
| 6 | SP-3 or SP-4 | Remediation | SP-1 |
| 7 | SP-5 | Performance | SP-1 |
| 8 | DB-4 | Performance | DB-3 |
| 9 | SP-6 | Performance | SP-3 or SP-4 |
| 10 | DB-5 | Performance | DB-4 |
| 11 | DB-6 | RT-core claim gate | DB-3, DB-4, RTX hardware |

---

## Verdict

**ACCEPT as action plan.** No new code is produced in this goal. This goal
produces the action plan that goal692+ should execute. The immediate next
coding goals are:

- Goal692: SP-1 + DB-1 correctness gate runs, SP-2 classification transparency,
  and SP-5 output-volume remediation for anyhit_rows.
- Goal693: DB-2 phase-split profiler and DB-3 prepared columnar dataset API.
- Goal694 (hardware-gated): SP-3 native OptiX segment/polygon kernel trial or
  SP-4 reclassification decision, followed by DB-6 RTX-class validation.

No OptiX app in the DB or segment/polygon threads should advance to an
`optix_traversal` RT-core performance claim before goal694 is complete.
