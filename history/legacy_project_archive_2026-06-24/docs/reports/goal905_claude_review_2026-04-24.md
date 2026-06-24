# Goal905 Graph Native OptiX Cloud-Gate Packaging — Claude Review

Date: 2026-04-24
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

---

## Scope

This review covers:

- `scripts/goal889_graph_visibility_optix_gate.py`
- `scripts/goal759_rtx_cloud_benchmark_manifest.py`
- `tests/goal889_graph_visibility_optix_gate_test.py`
- `tests/goal759_rtx_cloud_benchmark_manifest_test.py`
- `docs/reports/goal905_graph_native_optix_cloud_gate_packaging_2026-04-24.md`
- `docs/app_engine_support_matrix.md`
- `docs/reports/goal902_app_by_app_rt_usage_and_next_moves_2026-04-24.md`

---

## Gate Logic

### Scenario routing

`_run_optix_record` branches correctly:

- `visibility_edges` (not in `{"bfs", "triangle_count"}`): calls
  `graph_app.run_app("optix", "visibility_edges", ..., require_rt_core=True)`.
  `_enforce_rt_core_requirement` allows this only when `scenario ==
  "visibility_edges"`, so the RT-core flag is correctly scoped. Label is
  `optix_visibility_anyhit`.

- `bfs` and `triangle_count`: calls
  `graph_app.run_app("optix", scenario, ..., optix_graph_mode="native")`.
  This routes to the explicit native graph-ray path in the app. Labels are
  `optix_native_graph_ray_bfs` and `optix_native_graph_ray_triangle_count`.

### Digest computation

Both `_run_cpu_record` and `_run_optix_record` always call `graph_app.run_app`
with `output_mode="rows"`, so `_canonical` always computes `row_digest` from
full row data regardless of whether rows are included in the output artifact.
The `include_rows` flag only controls what is emitted to JSON. Row-level parity
is therefore always checked, even in summary-output runs. This is correct.

### Strict / non-strict behaviour

- Non-strict: OptiX failures are recorded as `status: "unavailable_or_failed"`
  and logged in `strict_failures`, but `status` is `"non_strict_recorded_gaps"`,
  not a hard failure. The gate continues.
- Strict: any absent or mismatched OptiX path triggers exit code 1 and
  `status: "fail"`. The `strict_pass` field is always written.

### No-speedup / no-cloud claims preserved

`rt_core_accelerated` is hardcoded `False` in `rtdl_graph_analytics_app.py`
regardless of backend or scenario. `honesty_boundary` explicitly states that
native graph-ray mode is gated and that only `visibility_edges` is the current
RT-core candidate. The gate's `cloud_claim_contract.non_claim` and `boundary`
fields repeat these exclusions. No timing delta or speedup claim is computed
anywhere in the gate output.

The app-engine support matrix correctly marks `graph_analytics` as
`direct_cli_compatibility_fallback` for OptiX (the default path is
host-indexed; native graph-ray is behind an explicit flag). The readiness
matrix keeps `graph_analytics` at `needs_real_rtx_artifact` with allowed
claim bounded to visibility filtering plus candidate-generation sub-paths,
explicitly excluding shortest-path, graph databases, distributed analytics,
and whole-app graph-system acceleration.

---

## Test Coverage

| Test | What it validates |
|---|---|
| `test_graph_app_visibility_edges_cpu_summary` | CPU reference row count and `rt_core_accelerated: False`; `honesty_boundary` contains "Only visibility_edges" |
| `test_require_rt_core_all_still_rejects_bfs_triangle_count` | `require_rt_core=True` for scenario "all" raises RuntimeError — BFS/triangle cannot be falsely promoted via the RT-core flag |
| `test_non_strict_gate_records_missing_optix_without_failing` | All three OptiX labels appear in `strict_failures` when OptiX is absent; non-strict status is `non_strict_recorded_gaps` |
| `test_strict_passes_when_optix_matches_cpu_digest` | Strict pass when CPU mock replays all three paths; BFS and triangle records carry `optix_graph_mode: "native"` |
| `test_cli_writes_non_strict_json` | End-to-end CLI run; output JSON contains `optix_native_graph_ray_bfs` and `optix_native_graph_ray_triangle_count` labels and `cloud_claim_contract` |
| `test_deferred_graph_entry_uses_goal889_gate` (manifest test) | Deferred manifest entry points to the right script with `--strict`; required baselines include CPU and native graph-ray references; `non_claim` contains "not shortest-path" |

All six tests are targeted and non-redundant. The `test_require_rt_core_all_still_rejects_bfs_triangle_count` test is particularly important: it prevents a future caller from using the `require_rt_core` flag to assert RT-core acceleration over BFS/triangle before the native path passes RTX validation.

---

## Manifest Contract

The Goal759 deferred entry for `graph_analytics`:

- Command uses `goal889_graph_visibility_optix_gate.py --strict --output-mode summary`
- `activation_gate` requires strict pass on RTX hardware for all three sub-paths
  plus independent review
- `claim_scope` is limited to visibility any-hit and native BFS/triangle candidate
  generation
- `non_claim` excludes shortest-path, graph database, distributed analytics,
  whole-app graph-system acceleration
- `baseline_review_contract.required_baselines` includes
  `cpu_python_reference_bfs`, `cpu_python_reference_triangle_count`,
  `optix_native_graph_ray_bfs`, `optix_native_graph_ray_triangle_count`, and
  `embree_graph_ray_bfs_and_triangle_when_available`

These are consistent with the gate logic and do not authorize a cloud speedup claim.

---

## Minor Observation (non-blocking)

`_enforce_rt_core_requirement` in `rtdl_graph_analytics_app.py` still prints
`"BFS and triangle_count remain host-indexed fallback today"` in its error
message. This is slightly stale now that an explicit native graph-ray path
exists; however, the conservative wording is intentional — the `require_rt_core`
flag is correctly not extended to those paths, and the native mode is accessed
via `optix_graph_mode="native"` instead. No behavior change is needed.

---

## Summary

The gate correctly routes all three graph sub-paths to their appropriate OptiX
call signatures, computes row-digest parity against CPU reference for each, and
preserves the no-speedup / no-cloud-claim boundary throughout. Test coverage
validates label assignment, `optix_graph_mode` tagging, and non-claim
enforcement. The manifest contract keeps the graph gate deferred pending real
RTX hardware validation and independent review.

**ACCEPT** — one short reason: all three graph RT sub-paths are correctly
validated by row digest with appropriate call signatures, no speedup claim is
made, and the promotion gate requires strict RTX artifact review.
