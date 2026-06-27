# Phoenix V3 M29 Draft Runbook: Barnes-Hut V2.14 / Current Focused POD Classification

Date: 2026-06-23
Status: `draft_pending_m28_2ai_consensus`

## Purpose

Run only the focused Barnes-Hut classification required by M28. Do not run
all-app. Do not make release or public speedup claims.

The question is narrow:

Does Phoenix V3's productized aggregate-tree fused weighted-vector runtime
trunk add a real, app-agnostic V3 capability over the V2.14 surface, while
preserving the current high-speed fused Numba CUDA route?

## POD Budget

Expected POD use:

- checkout/build/probe: 0.25-0.5 hours;
- v2.14 surface classification and small smoke: 0.25-0.5 hours;
- current focused runner/control rerun, if needed: 0.25-0.5 hours;
- total expected: 0.5-1.5 POD hours.

At `$1 / 4 hours`, expected cost is `$0.13-$0.38`.

Stop early if v2.14/current cannot be built or imported cleanly on the pod
within the first 0.5 POD hours; record the blocker instead of drifting into
environment work.

## Inputs

POD access, if still current:

`ssh root@213.173.108.14 -p 11592 -i ~/.ssh/id_ed25519_rtdl_codex_current_pod`

Current Phoenix V3 working tree:

`C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`

Frozen M28 packet:

`docs/rebuild/v3/phoenix_v3_m28_set_a_trunk_family_freeze_aggregate_tree_fused_vector_sum_2026-06-23.md`

## Required Classification Before Timing

In a clean pod workspace, inspect `v2.14` and current separately. Record:

- `git rev-parse v2.14`
- current source provenance
- when citing M28 fixed evidence, restate that the local base commit is
  `8e0f052bffec02507aaf5ed05f75dfe995f39883` and that the remote execution
  tree recorded `git_commit: null` because it was not a git checkout
- mode list for `examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py`
- existence or absence of:
  - `prepared_execution_fused_vector_sum_numba_cuda`
  - `fused_frontier_force_sum_bucketized_numba_cuda`
  - `fused_frontier_force_sum_bucketized_cpu`
  - `grouped_vector_sum_typed_stream_plan`
  - `embree_node_coverage_prepared`
  - `optix_node_coverage_prepared`
  - `run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session`

Write one classification:

- `v2_14_lacks_current_trunk_surface`
- `v2_14_has_equivalent_fused_surface`
- `v2_14_has_cpu_fused_or_typed_stream_only`
- `v2_14_has_only_node_coverage_or_frontier_route`
- `blocked_environment_or_build`

## Allowed Timing Rows

If v2.14 lacks an equivalent Numba CUDA fused route:

- do not claim same-contract speedup for current runner vs v2.14;
- rerun current runner/control only if current evidence must be refreshed;
- if citing `runtime_sourced_material_gain: true` from the M28 evidence
  `summary.json`, state that it is keyed to historical OptiX/frontier
  displacement, not current runner/control parity;
- if timing rows use `validation_skipped: true`, state what validation was
  skipped and which summary-level equivalence gate replaces it;
- optionally record v2.14 CPU fused or node-coverage rows as contract-bound
  reference rows only.

If v2.14 has an equivalent fused route under another name:

- compare current runner against v2.14 equivalent route at body counts
  `32768`, `65536`, `131072`;
- use hot-call wall medians;
- require output equivalence when output contracts permit;
- require every row `>=0.95x`, geomean `>=0.98x`;
- require `>=1.15x` geomean before any material-speed classification.

Current runner/control refresh, if needed:

`python3 scripts/v3_phoenix_barnes_hut_runner_parity_pod_ab.py --output-dir <evidence-dir> --body-counts 32768 65536 131072 --query-repeat 11 --warmup 3 --samples 5`

## Required Evidence Fields

The report must include:

- POD GPU and driver;
- source provenance for both trees;
- OptiX/Embree build provenance if used;
- exact command lines;
- timing medians and sample counts;
- runner metadata gates;
- output equivalence gates;
- classification label;
- all non-authorization flags.

Runner-gate fields must include or derive:

- `prepared_execution_session_runner_used=True`
- `runtime_trunk_executes_end_to_end=True`
- `internal_device_residency_between_rtdl_phases=True`
- `frontier_rows_materialized_on_host=False`
- `contribution_rows_materialized_on_host=False`
- `hot_path_host_materialization=False`
- explicit partner `numba_cuda`
- no automatic partner selection

## Stop Conditions

Stop immediately and write a blocker if:

- M28 external review is not accepted;
- v2.14/current comparison would mix different contracts without labeling them;
- current runner/control parity falls below M28 floors;
- output equivalence fails;
- any report text tries to claim RT-core speedup for the Numba CUDA fused route;
- all-app timing is requested before two accepted Set-A families exist.

## Goal-Level Decision Audit

Decision: prepare M29 as a focused classification run, not a benchmark sweep.

1. Was I foolish?
   No. This prevents another uncontrolled all-app or mixed-contract run.

2. If yes, what actions made the decision foolish?
   The foolish action would be spending POD hours before M28 consensus or using
   a v2.14 node-coverage row as if it were the same fused force-vector contract.

3. Was there another path?
   Yes. Run all-app immediately. That path is rejected until two Set-A families
   are accepted.

4. Can I now try a different path that truly solves the problem?
   Yes. First classify the v2.14 surface, then time only the rows that answer
   the trunk question.

## Non-Authorization

This runbook authorizes no release, no all-app run, no public speedup claim, no
broad V3-over-V2 claim, no RT-core speedup claim, no true-zero-copy claim, and
no V4 work.
