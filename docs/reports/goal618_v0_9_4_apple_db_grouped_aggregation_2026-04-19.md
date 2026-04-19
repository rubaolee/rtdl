# Goal618: v0.9.4 Apple DB `grouped_count` / `grouped_sum`

Date: 2026-04-19

Status: accepted with 2-AI consensus (Codex + Gemini 2.5 Flash bounded review).

## Scope

Goal618 adds bounded Apple native-assisted support for DB grouped aggregation:

- `grouped_count`
- `grouped_sum`

This goal reuses Goal617's Apple Metal compute predicate filter and performs deterministic grouped aggregation on CPU.

This is not full-GPU aggregation.

## Implemented Surface

Python wrapper:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`
- `grouped_count_apple_rt(table_rows, query)`
- `grouped_sum_apple_rt(table_rows, query)`

Public export:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`

Tests:

- `/Users/rl2025/rtdl_python_only/tests/goal618_apple_rt_db_grouped_aggregation_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal582_apple_rt_full_surface_dispatch_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal603_apple_rt_native_contract_test.py`

## Lowering

The bounded lowering is:

```text
GroupedQuery + DenormTable
  -> normalize grouped query
  -> Apple Metal compute numeric predicate filtering through Goal617
  -> CPU deterministic group-count/group-sum aggregation over filtered rows
  -> emit grouped rows
```

Supported:

- numeric predicate filtering through the Goal617 Metal compute path
- text or numeric group keys, because aggregation remains CPU-side
- numeric sum value fields, following the existing CPU grouped-sum rules

Out of scope:

- GPU hash/group aggregation
- GPU atomics for grouped reductions
- text/date predicate filtering
- PostgreSQL replacement claims
- MPS RT DB traversal claims

## Support Matrix Change

`grouped_count` and `grouped_sum` are now marked:

```text
mode: native_metal_filter_cpu_aggregate
native_candidate_discovery: no
cpu_refinement: cpu_group_aggregation_after_metal_filter
native_only: supported_for_numeric_predicates_cpu_aggregation
```

This is a native-assisted status. It means the predicate-filter phase is Apple Metal compute backed, while aggregation remains CPU deterministic.

The graph rows remain compatibility-only:

- `bfs_discover`
- `triangle_match`

## Validation

Python syntax check:

```bash
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/apple_rt_runtime.py src/rtdsl/__init__.py tests/goal618_apple_rt_db_grouped_aggregation_test.py tests/goal603_apple_rt_native_contract_test.py
```

Result: passed.

Goal618 focused suite:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal618_apple_rt_db_grouped_aggregation_test tests.goal617_apple_rt_db_conjunctive_scan_test tests.goal603_apple_rt_native_contract_test -v
```

Result:

```text
Ran 18 tests in 0.076s
OK
```

Apple native coverage regression suite:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test tests.goal582_apple_rt_full_surface_dispatch_test tests.goal596_apple_rt_prepared_closest_hit_test tests.goal597_apple_rt_masked_hitcount_test tests.goal598_apple_rt_masked_segment_intersection_test tests.goal603_apple_rt_native_contract_test tests.goal604_apple_rt_ray_hitcount_2d_native_test tests.goal605_apple_rt_point_neighbor_2d_native_test tests.goal606_apple_rt_point_neighbor_3d_native_test tests.goal607_apple_rt_point_in_polygon_positive_native_test tests.goal608_apple_rt_segment_polygon_native_test tests.goal609_apple_rt_point_nearest_segment_native_test tests.goal610_apple_rt_polygon_pair_native_test tests.goal611_apple_rt_overlay_compose_native_test tests.goal616_apple_rt_compute_skeleton_test tests.goal617_apple_rt_db_conjunctive_scan_test tests.goal618_apple_rt_db_grouped_aggregation_test -v
```

Result:

```text
Ran 65 tests in 0.256s
OK
```

Coverage included:

- direct grouped count equals CPU grouped count
- direct grouped sum equals CPU grouped sum
- `run_apple_rt(..., native_only=True)` grouped count equals CPU reference
- `run_apple_rt(..., native_only=True)` grouped sum equals CPU reference
- 4096-row grouped count/sum stress parity
- text predicate rejection
- support-matrix contract update
- compatibility-only graph rows still reject native-only

## Honesty Boundary

Goal618 should be described as Apple Metal-filtered, CPU-aggregated grouped DB execution.

It should not be described as:

- full Apple GPU grouped aggregation
- MPS RT DB traversal
- a database engine
- a PostgreSQL replacement
- a performance win

## Codex Verdict

Accept as the implementation half of Goal618.

Reason: the implementation extends the Goal617 filter path without overclaiming aggregation. It provides exact CPU parity and explicit support-matrix language for native-assisted execution. Goal618 should be called closed only after external AI review accepts this boundary.

## External Review

External review record:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal618_external_review_2026-04-19.md`

Gemini 2.5 Flash returned `ACCEPT` on a bounded evidence review. Goal618 is accepted only as Apple Metal predicate filtering plus CPU aggregation. It does not close full-GPU aggregation, MPS RT DB traversal, graph workloads, or performance claims.
