# Phoenix V3 AABB Count Runner / LibRTS Route M4

Date: 2026-06-22
Status: `m4_aabb_count_runner_librts_route_local_contract_not_pod_evidence_not_release`
Scope: Phoenix V3 generic runtime work only.

## Summary

After M3.4 showed RTDBSCAN repeated-runner parity but no material Set-A win,
the next Phoenix V3 generic-runtime path is AABB runner generalization.

M4 adds a count-only AABB prepared-session runner helper and wires the LibRTS
Embree count route through it:

```text
run_aabb_index_query_2d_count_prepared_session(...)
```

This is local contract progress only. It is not pod performance evidence, not a
second material Set-A probe, not release authorization, and not full all-app pod
rerun authorization.

## Why This Was Needed

M2/M2.1 proved the runner can carry generic AABB `range_intersection_rows`
through the Contact Manifold harness. That was the first material
productized-path focused win on the pod.

But LibRTS-style spatial indexing is mostly count-only:

```text
point_contains
range_contains
range_intersects
all
```

The existing AABB helper only covered row output:

```text
run_aabb_index_query_2d_range_intersection_prepared_session(...)
```

So AABB was not yet a generic primitive family inside the runner. M4 closes the
local contract gap for count-only AABB workloads.

## Code Changes

Files changed:

```text
src/rtdsl/prepared_execution.py
src/rtdsl/__init__.py
examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py
tests/v3_phoenix_prepared_execution_session_runner_test.py
tests/v3_phoenix_librts_aabb_count_runner_test.py
```

New exported helper:

```text
run_aabb_index_query_2d_count_prepared_session
```

Supported operation values:

```text
all
point_contains
range_contains
range_intersects
```

The helper records:

```text
primitive: aabb_index_query_2d_native_query_handle
primitive_family: aabb_index_query_2d_native_query_handle
productized_execution_path: prepared_execution_session_runner
row_contract: generic_prepared_aabb_index_query_2d_count
count_contract: generic_prepared_aabb_index_query_2d_count
set_a_probe_candidate: true
full_all_app_rerun_authorized_by_this_packet: false
```

Claim flags remain false:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
automatic_partner_selection_authorized: false
app_specific_native_engine_logic_allowed: false
```

## LibRTS Route Wiring

`run_embree_aabb_counts(...)` now calls:

```text
rt.run_aabb_index_query_2d_count_prepared_session(
    indexed_boxes=fixture.boxes,
    point_queries=fixture.point_queries,
    box_queries=fixture.box_queries,
    operation=operation,
    backend="embree",
    partner="none",
    cache=cache,
    warmup_count=warmup,
    measured_repeat_count=query_repeat,
    retain_repeat_outputs=True,
)
```

The route no longer hand-rolls the measured repeat loop for Embree. The
prepared execution/session runner owns:

```text
one cache lookup / prepare
warmup repeats
measured repeats
one report payload
```

The LibRTS payload now records:

```text
prepared_execution_session_runner_used: true
productized_execution_path: prepared_execution_session_runner
prepared_execution_session_runner_metadata
```

The route still keeps the benchmark boundary:

```text
native_engine_customization: false
authors_code_comparison: false
paper_reproduction: false
public_speedup wording unauthorized
```

## What Was Not Changed

M4 does not replace the existing OptiX LibRTS prepared-query-set route yet.

Reason:

```text
The OptiX route has a separate prepared-query-set fast path
count_prepared_query_set / count_prepared_queries.
Replacing it with a simpler generic count wrapper could regress performance.
```

The next AABB generalization step should design a productized runner wrapper
for the OptiX prepared-query-set count path rather than silently downgrading the
incumbent route.

## Validation

Focused local tests:

```text
PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test
Ran 15 tests
OK

PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_librts_aabb_count_runner_test \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_aabb_prepared_query_cache_test
Ran 22 tests
OK

PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_rtdbscan_component_signature_optimization_test \
  tests.v3_phoenix_set_ab_scorecard_gate_test \
  tests.v3_phoenix_aabb_prepare_reuse_pod_runner_test \
  tests.v3_phoenix_aabb_prepared_query_cache_test \
  tests.v3_phoenix_librts_aabb_count_runner_test
Ran 32 tests
OK
```

Syntax check:

```text
py -3 -m py_compile \
  src/rtdsl/prepared_execution.py \
  src/rtdsl/__init__.py \
  examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py \
  tests/v3_phoenix_librts_aabb_count_runner_test.py
OK
```

## Classification

```text
local_contract_progress: true
pod_performance_evidence: false
second_material_set_a_probe_obtained: false
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
full_all_app_pod_rerun_authorized: false
```

## Next Required Work

1. Design an OptiX prepared-query-set count runner wrapper without degrading
   the incumbent fast path.
2. Add a LibRTS OptiX route contract test proving runner metadata is visible.
3. Run a focused same-pod A/B for LibRTS/AABB count-only runner route only
   after the OptiX path is productized.
4. Treat it as material only if it beats the relevant incumbent route, not
   merely a weaker CPU/Embree control.

## Goal-Level Decision Audit

Decision: after RTDBSCAN M3.4 reached parity but no material win, redirect to
AABB generalization by adding a generic count-only AABB prepared-session helper
and wiring the LibRTS Embree count route through it.

1. Was I foolish?
   No. This targets a reusable AABB primitive family, not an app-specific
   LibRTS shortcut.
2. If yes, what actions made the decision foolish?
   The foolish action would have been to continue RTDBSCAN micro-tuning after
   the measured `0.9976x` runner-vs-legacy result, or to replace the OptiX
   prepared-query-set fast path without a design.
3. Was there another path that avoids being stuck on a foolish idea?
   Yes. Keep the current OptiX incumbent route intact, productize count-only
   AABB at contract level first, and require focused pod A/B before calling it
   performance.
4. Can I now try a different path that truly solves the problem?
   Yes. The next path is an OptiX prepared-query-set runner wrapper and a
   focused LibRTS/AABB pod A/B against the relevant incumbent.
