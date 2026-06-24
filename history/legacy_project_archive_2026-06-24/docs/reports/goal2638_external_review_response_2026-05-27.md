# Goal2638 External Review Response

Date: 2026-05-27

Scope: `AGGREGATE_FRONTIER_COLLECT_2D`, Barnes-Hut aggregate-frontier
collection, partner-column adapter, primitive hierarchy entry, documentation,
and regression tests.

## Review Sources

Two external review rounds were received through user-pasted review output:

- Review round 1, Gemini 3.1 Pro: accepted the primitive direction but
  required schema extensibility, stricter diagnostic boundaries,
  exact-capacity tests, and clearer native-backend disclosure.
- Review round 2, Claude: re-reviewed the changed on-disk state, kept the
  verdict at accept-with-fixes, and raised two blocking issues: undocumented
  `metadata_flags` and Barnes-Hut inverse-square force helpers still living in
  the aggregate-tree engine module.

Both review rounds are summarized in:

`docs/reports/goal2638_claude_critical_review_2026-05-27.md`

Note: the file name is retained for continuity, but the file now records both
Gemini 3.1 Pro and Claude review rounds.

3-AI consensus is recorded in:

`docs/reports/goal2638_3ai_consensus_2026-05-27.md`

## Codex Position

Codex accepts the architectural direction and the blocking findings.

The correct boundary is:

- RTDL may own aggregate-tree traversal, source offsets, row-major frontier ID
  layout, capacity checks, and app-independent backend planning.
- RTDL native engines must not own Barnes-Hut force law, inverse-square
  scoring, mass multiplication, timestep integration, or app-specific
  reductions.
- Python app/reference code may implement Barnes-Hut force math, but it must be
  labeled as app-reference behavior rather than an engine primitive.
- Native Embree/OptiX lowering for `AGGREGATE_FRONTIER_COLLECT_2D` remains
  future work and has no RT-core speedup claim.

## Response Matrix

| Review finding | Codex response | Status |
| --- | --- | --- |
| Six-field schema had no reserve/version lane. | Added reserved `metadata_flags` to `AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA` and every `frontier_i64_rows` record. | Resolved |
| `metadata_flags` became undocumented after first fix. | Exported `AGGREGATE_FRONTIER_COLLECT_ROW_METADATA_FLAGS_NONE`; documented `0 = no flags set`; required partners to ignore unknown future non-zero flags unless a later contract revision defines them. | Resolved |
| Default `frontier_rows` leaked `distance` and `opening_ratio`. | Removed those fields from default rows; added opt-in `include_debug_diagnostics=True` side channel. | Resolved |
| Debug diagnostics were untested. | Added tests for default absence, opt-in presence, row count parity, `distance`, and `opening_ratio`. | Resolved |
| Exact-capacity overflow boundaries were weak. | Added total exact-capacity and per-source exact-capacity tests; fail-closed overflow still raises before result materialization. | Resolved |
| Overflow messages said "emitted" even though partial rows are abandoned. | Changed wording to "attempted" for total and per-source overflow messages. | Resolved |
| Force-math functions lived in `src/rtdsl/aggregate_tree_reference.py`. | Moved inverse-square force/reference helpers to `src/rtdsl/app_reference/aggregate_force_math.py`. | Resolved |
| Existing examples/tests depended on top-level `rtdsl.*` force helpers. | Kept top-level compatibility exports, now sourced from `rtdsl.app_reference`, so existing callers keep working while the engine module is clean. | Resolved |
| Primitive hierarchy outputs omitted schema fields. | Expanded `rows.aggregate_frontier_collect` outputs to include all schema fields plus `row_offsets`. | Resolved |
| `partner_resident_ready` over-suggested device residency. | Renamed metadata to `partner_i64_row_layout_ready`; claim boundary explicitly excludes device-resident/native execution claims. | Resolved |
| Partner adapter surfaced `metadata_flags` without guidance. | Added `metadata_flags_semantics` to collection metadata, columnar adapter metadata, partner adapter metadata, report, catalog, and README. | Resolved |
| Extra `frontier_rows` fields could be mistaken for stable schema. | Recorded `frontier_row_extra_fields_reference_only` metadata; tests use `frontier_kind_code` for kind dispatch instead of the string alias. | Resolved |
| Missing edge coverage for single-body and dedup toggle. | Added tests for single-body empty output and `deduplicate_fallback_targets=False`. | Resolved |
| Missing i64 checks for kind codes, `resume_index=-1`, and offset slices. | Added tests for kind-code subset, exact fallback kind presence, leaf sentinel `-1`, `metadata_flags=0`, and per-source offset slicing. | Resolved |
| Documentation under-disclosed native backend status. | Report, README, and catalog now state that CPU reference and partner-column layout exist; Embree/OptiX lowering is future work. | Resolved |

## Implementation Response

Files changed for the Goal2638 review response:

- `src/rtdsl/aggregate_tree_reference.py`: keeps aggregate-tree and
  `AGGREGATE_FRONTIER_COLLECT_2D` contract logic; no inverse-square force
  helper remains there.
- `src/rtdsl/app_reference/aggregate_force_math.py`: new app-reference module
  for Barnes-Hut inverse-square contribution rows, vector sums, materialization
  pressure, and fused reference sums.
- `src/rtdsl/app_reference/__init__.py`: explicit app-reference export surface.
- `src/rtdsl/__init__.py`: keeps compatibility exports but imports force-math
  helpers from `rtdsl.app_reference`.
- `src/rtdsl/partner_adapters.py`: adds aggregate-frontier partner-column
  adapter metadata for `metadata_flags`.
- `src/rtdsl/primitive_hierarchy.py`: records full aggregate-frontier collect
  row outputs.
- `tests/goal2638_aggregate_frontier_collect_test.py`: adds the expanded
  review-driven regression suite.
- `docs/reports/goal2638_aggregate_frontier_collect_2026-05-27.md`: records the
  final contract and boundary.
- `docs/reports/goal2638_claude_critical_review_2026-05-27.md`: records the
  Gemini 3.1 Pro and Claude review findings and action status.
- `docs/reports/goal2638_3ai_consensus_2026-05-27.md`: records the final Codex
  plus Gemini 3.1 Pro plus Claude consensus boundary.
- `docs/rtdl_primitive_catalog.md` and
  `examples/v2_0/research_benchmarks/barnes_hut/README.md`: document the
  candidate behavior and claim boundary.

## Verification

Commands run after remediation:

```bash
PYTHONPATH=src:. python3 - <<'PY'
import rtdsl as rt
print(rt.AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA)
print(rt.AGGREGATE_FRONTIER_COLLECT_ROW_METADATA_FLAGS_NONE)
print(rt.WEIGHTED_INVERSE_SQUARE_VECTOR_SUM_2D_CONTRACT)
print(rt.sum_weighted_inverse_square_contributions_2d.__module__)
PY

PYTHONPATH=src:. python3 -m unittest tests.goal2638_aggregate_frontier_collect_test

PYTHONPATH=src:. python3 -m unittest \
  tests.goal2538_barnes_hut_fused_frontier_vector_sum_test \
  tests.goal2549_native_engine_boundary_rejection_test \
  tests.goal2624_primitive_hierarchy_test

PYTHONPATH=src:. python3 -m unittest \
  tests.goal2531_barnes_hut_generic_opening_rows_test \
  tests.goal2532_barnes_hut_benchmark_app_completion_test \
  tests.goal2533_barnes_hut_generic_force_contributions_test \
  tests.goal2534_barnes_hut_streamed_vector_sum_test \
  tests.goal2535_barnes_hut_materialization_pressure_test \
  tests.goal2539_barnes_hut_same_contract_cpp_baseline_test \
  tests.goal2540_barnes_hut_benchmark_app_closeout_test \
  tests.goal1979_exact_pairwise_force_partner_barnes_hut_reference_test

git diff --check
```

Observed result: all listed tests passed and `git diff --check` reported no
whitespace errors.

## Remaining Boundary

This response does not promote native aggregate-frontier execution.

Still future work:

- app-name-free Embree symbol for aggregate-frontier collect;
- app-name-free OptiX symbol for aggregate-frontier collect;
- same-contract CPU/Embree/OptiX parity evidence;
- pod timing evidence before RT-core performance wording;
- external review before any promotion from candidate behavior.

Goal2638 is therefore accepted only as a CPU-reference and partner-column
layout contract, not as a native RT backend or Barnes-Hut speedup claim.
