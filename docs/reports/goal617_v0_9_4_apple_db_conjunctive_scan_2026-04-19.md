# Goal617: v0.9.4 Apple DB `conjunctive_scan` Native-Assisted Slice

Date: 2026-04-19

Status: accepted with 2-AI consensus (Codex + Gemini 2.5 Flash bounded review).

## Scope

Goal617 adds the first Apple graph/DB workload from the v0.9.4 plan: bounded numeric `conjunctive_scan`.

This is Apple GPU-backed through Metal compute. It is not MPS RT traversal and it is not a full database system.

## Implemented Surface

Native entry point:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_apple_rt.mm`
- `rtdl_apple_rt_run_db_conjunctive_scan_numeric_compute(...)`

Python wrapper:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`
- `conjunctive_scan_apple_rt(table_rows, predicates)`

Public export:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`

Tests:

- `/Users/rl2025/rtdl_python_only/tests/goal617_apple_rt_db_conjunctive_scan_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal603_apple_rt_native_contract_test.py`

## Lowering

The bounded lowering is:

```text
DenormTable + PredicateSet
  -> Python schema/row_id/predicate normalization
  -> float32 numeric predicate-field buffers
  -> Metal compute predicate filtering, one thread per row
  -> native matched row_id compaction
  -> Python row_id tuple materialization
```

Supported predicate operators:

- `eq`
- `lt`
- `le`
- `gt`
- `ge`
- `between`

Supported values:

- `bool`
- bounded exact `int` values within float32 exact integer range
- finite `float` values

Out of scope for this first slice:

- text predicates
- dates/strings without explicit encoding
- full SQL semantics
- PostgreSQL execution on macOS
- grouped aggregation
- MPS RT candidate discovery

## Support Matrix Change

`conjunctive_scan` is now marked:

```text
mode: native_metal_compute
native_candidate_discovery: no
cpu_refinement: row_id_materialization_only
native_only: supported_for_numeric_predicates
```

This is intentionally different from `native_mps_rt`. The main predicate/filter work runs on Apple Metal compute, not on MPSRayIntersector.

The remaining graph/DB rows stay compatibility-only:

- `grouped_count`
- `grouped_sum`
- `bfs_discover`
- `triangle_match`

## Validation

Build:

```bash
make build-apple-rt
```

Result: passed.

Python syntax check:

```bash
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/apple_rt_runtime.py src/rtdsl/__init__.py tests/goal617_apple_rt_db_conjunctive_scan_test.py
```

Result: passed.

Goal617 tests:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal617_apple_rt_db_conjunctive_scan_test -v
```

Result:

```text
Ran 7 tests in 0.029s
OK
```

Focused Apple regression suite:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal616_apple_rt_compute_skeleton_test tests.goal617_apple_rt_db_conjunctive_scan_test tests.goal582_apple_rt_full_surface_dispatch_test tests.goal603_apple_rt_native_contract_test -v
```

Result:

```text
Ran 19 tests in 0.086s
OK
```

Apple native coverage regression suite:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test tests.goal582_apple_rt_full_surface_dispatch_test tests.goal596_apple_rt_prepared_closest_hit_test tests.goal597_apple_rt_masked_hitcount_test tests.goal598_apple_rt_masked_segment_intersection_test tests.goal603_apple_rt_native_contract_test tests.goal604_apple_rt_ray_hitcount_2d_native_test tests.goal605_apple_rt_point_neighbor_2d_native_test tests.goal606_apple_rt_point_neighbor_3d_native_test tests.goal607_apple_rt_point_in_polygon_positive_native_test tests.goal608_apple_rt_segment_polygon_native_test tests.goal609_apple_rt_point_nearest_segment_native_test tests.goal610_apple_rt_polygon_pair_native_test tests.goal611_apple_rt_overlay_compose_native_test tests.goal616_apple_rt_compute_skeleton_test tests.goal617_apple_rt_db_conjunctive_scan_test -v
```

Result:

```text
Ran 58 tests in 0.221s
OK
```

Coverage included:

- direct Apple numeric scan equals CPU reference
- `run_apple_rt(..., native_only=True)` equals CPU reference
- bounded 4096-row stress parity
- float predicate fixture
- empty predicate bundle returns all row IDs
- text predicate rejection
- support-matrix contract update

## Honesty Boundary

Goal617 should be described as Apple Metal compute DB predicate filtering.

It should not be described as:

- Apple MPS RT DB traversal
- a database system
- a PostgreSQL replacement
- a broad DB performance win
- support for grouped DB aggregation

No performance claim is made here beyond the fact that the predicate/filter stage is executed by Apple Metal compute.

## Codex Verdict

Accept as the implementation half of Goal617.

Reason: the implementation is bounded, test-backed, and honest about its Apple GPU compute mode. Goal617 should be called closed only after external AI review accepts this same boundary.

## External Review

External review record:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal617_external_review_2026-04-19.md`

Gemini 2.5 Flash returned `ACCEPT` on a bounded evidence review. Goal617 is accepted only for bounded numeric `conjunctive_scan` through Apple Metal compute. It does not close grouped DB aggregation, graph workloads, MPS RT DB traversal, or any performance claim.
