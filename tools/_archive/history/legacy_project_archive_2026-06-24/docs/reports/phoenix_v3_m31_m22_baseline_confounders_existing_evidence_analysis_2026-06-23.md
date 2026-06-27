# Phoenix V3 M31 M22 Baseline Confounders Existing-Evidence Analysis

Date: 2026-06-23

Status: `m22_baseline_confounders_identified_not_closed_not_release`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
new_pod_run_performed: false
```

## Scope

This is a local analysis of existing M22 all-app evidence. It does not run POD
and does not change release status.

Evidence inspected:

- `docs/rebuild/v3/evidence/phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315`
- `docs/reports/phoenix_v3_m22_all_app_pod_result_2026-06-23.md`
- `docs/reviews/codex_claude_phoenix_v3_m22_all_app_result_2ai_consensus_2026-06-23.md`

## Confounder 1: Current RayJoin Point-Order Bug

M22 current row:

```text
app_id: spatial_rayjoin
case_id: rayjoin_optix_promoted_overlay_seed_tiled_x2048
status: failed
returncode: 1
```

Error:

```text
TypeError: run_rayjoin_prepared_optix_shape_pair_active_count_workload()
got an unexpected keyword argument 'point_order_mode'
```

Status after M22:

- M23 fixed this current V3 RayJoin defect and obtained Codex + Claude
  consensus.
- This row was a current-code correctness defect and cannot be used as a
  performance result until rerun under the fixed route.

## Confounder 2: V2.14 Spatial RayJoin OptiX Failure

M22 V2.14 row:

```text
app_id: spatial_rayjoin
case_id: spatial_rayjoin_optix_prepared_full_route
status: failed
returncode: 1
```

Error:

```text
RuntimeError: OptiX error: Invalid value
```

Interpretation:

- This is a V2.14 baseline failure on the M22 pod/harness combination.
- It does not prove current V3 is faster or slower.
- Before another all-app comparison, this row must be either repaired,
  excluded with explicit justification, or replaced by a verified same-contract
  baseline row.

## Confounder 3: V2.14 Triangle OptiX PTX/Toolchain Failure

M22 V2.14 rows:

```text
triangle_counting_optix_rt_graph_2a1_partner
triangle_counting_optix_rt_graph_2a1_cliques_20000
triangle_counting_optix_rt_graph_2a1_cliques_80000
```

Error:

```text
CUDA error during launching 3-D ray-column pack kernel:
the provided PTX was compiled with an unsupported toolchain.
```

Interpretation:

- This is a V2.14 baseline environment/toolchain failure, not a measured
  current V3 speed result.
- It explains why Triangle rows are confounding in M22.
- It must be handled before any V2.14/current Triangle comparison is used in a
  release-adjacent scorecard.

## What Is Already Closed

M23 closed the current V3 RayJoin `point_order_mode` defect. That does not close
the V2.14 Spatial RayJoin OptiX baseline failure.

M19 closed a focused current Triangle productized-runner probe after
environment-corrected POD review. That does not close the M22 V2.14 Triangle
OptiX PTX/toolchain baseline failure.

## Next Engineering Direction

Before another all-app run:

1. Decide whether V2.14 failed rows are repaired or formally excluded.
2. If repaired, run focused baseline-only checks first, not full all-app.
3. Keep each failure separate from Phoenix V3 runtime-trunk proof:
   - current RayJoin bug: fixed by M23;
   - V2.14 Spatial RayJoin OptiX invalid value: still open;
   - V2.14 Triangle OptiX PTX/toolchain failure: still open.

## Goal-Level Decision Audit

Decision: keep M22 baseline confounders open and require focused baseline
repair/exclusion before another all-app comparison.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   The foolish action would be treating failed V2.14 rows as V3 performance
   wins or folding them into a broad geomean without repair/exclusion.

3. Was there another path?

   Yes: rerun all-app and hope the rows disappear. That would waste POD and
   repeat M22's interpretability problem.

4. Can I now try a different path that actually solves the problem?

   Yes. Isolate baseline failures, repair or exclude them under review, and
   only then permit another serious all-app comparison.
