# Goal3802 RayDB Current Helper Alias Cleanup

Date: 2026-06-07

## Purpose

Goal3802 extends the Goal3800 legacy-helper cleanup to RayDB's app-facing
helper layer. RayDB still needs historical protocol identifiers because many
reports and tests refer to the v2.5/v2.6/v2.8 milestones that introduced
primitive-first planning, Numba neutral handoff, and typed-stream grouped
reduction. But users should not have to call only version-stamped helper names
when using the current source-tree example.

## Added Current Aliases

| Current helper | Legacy helper preserved | Contract |
| --- | --- | --- |
| `describe_raydb_primitive_first_plan(...)` | `describe_raydb_v2_5_primitive_first_plan(...)` | Select the fused generic grouped-reduction primitive when it covers the query. |
| `describe_raydb_numba_grouped_reduction_continuation(...)` | `describe_raydb_v2_6_numba_neutral_continuation(...)` | Describe explicit Numba grouped-reduction continuation over caller-supplied device columns. |
| `run_raydb_numba_grouped_reduction_continuation_preview(...)` | `run_raydb_v2_6_numba_neutral_continuation_preview(...)` | Execute the same Numba path while recording a current execution-path alias. |
| `describe_raydb_grouped_reduction_typed_stream_continuation(...)` | `describe_raydb_v2_8_typed_stream_continuation(...)` | Describe the grouped-reduction typed-stream front door with a current helper name. |
| `run_raydb_grouped_reduction_typed_stream_continuation_preview(...)` | `run_raydb_v2_8_typed_stream_continuation_preview(...)` | Execute the same typed-stream path while recording a current execution-path alias. |

## Boundaries

- No native engine code changed.
- No RayDB, SQL, table, or database semantics moved into the engine.
- No release, package-install, zero-copy, RT-core speedup, or public speedup
  claim is authorized.
- Historical protocol names remain in constants, artifact keys, and internal
  helpers where changing them would break existing evidence.

## Validation

- `py -3 -m py_compile examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `tests.goal3802_raydb_current_helper_alias_cleanup_test`
- Existing RayDB typed-stream and Numba neutral tests remain compatible.
