# Phoenix V3 M14 Runtime-Trunk Retarget Status

Date: 2026-06-22
Status: `m14_runtime_trunk_status_reconciled_need_third_strict_probe_not_release`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
external_embedding_or_zero_copy_claim_authorized: false
all_app_pod_spend_authorized: false
focused_pod_spend_authorized_now: false
```

## Why This Exists

M13 closed Spatial LSI as coverage-only after a speed fail. The repo also
contains later runtime-trunk evidence for RTDBSCAN, RayJoin, Barnes-Hut, RTNN,
and Hausdorff. This report reconciles those facts before any new POD decision.

Do not resume Spatial LSI speed work from M13. Do not rerun RayJoin PIP or
RTDBSCAN wrapper probes hoping for noise. Do not run all-app until a status-gate
review says the focused evidence is sufficient to prepare that protocol.

## Probe Ledger

| Probe | Classification | Key Result | Review |
| --- | --- | --- | --- |
| Spatial LSI M13 | coverage only, speed fail | runner/old hot `0.785772x`; M13-vs-M11 runner improved `1.295618x` | `accept_m13_stop_spatial_retarget` |
| RTDBSCAN Step 1 | structural runtime trunk, not material | runner vs legacy `0.994858x`; legacy already beats Embree | `approve_blocked_not_release` |
| RayJoin PIP Step 2 | structural runtime trunk, not material | runner vs legacy total-repeat `0.973754x` | structural-only no-go |
| Barnes-Hut Step-1 replacement | productized runner carries real fused route at parity | runner vs existing fused control `0.999328x`; historical OptiX/runner `12.730691x` | `accept_ready_for_pod_report` |
| RTNN repeat50 Step 2 | accepted Set-A material probe, not release | runner vs legacy runner-wall `1.370176x`; cold-plus-query `1.358329x`; hot `0.988781x` | `accept_as_second_set_a_material_probe` |
| Hausdorff M6.1 | positive focused runner-backed probe, not release | runner vs legacy wrapper wall `1.054105x`; runner vs Embree wrapper wall `1.537811x` | accepted positive focused probe |

## Current Interpretation

Phoenix V3 now has real runtime-trunk progress, but it is still not release
ready.

- Spatial LSI: productized-runner coverage only; no speed credit.
- RTDBSCAN: runner executes and residency is visible; material speed did not
  appear because the incumbent already had the key physical advantage.
- RayJoin PIP: runner executes but wraps an already optimized scalar-count
  executor; no material speed source.
- Barnes-Hut: productized runner carries the high-performance fused
  vector-accumulation path without losing speed, and displaces the historical
  frontier-emission no-go route.
- RTNN: accepted as the second Set-A material probe on cold-plus-query and
  runner-wall metrics, with signature parity against legacy and CuPy.
- Hausdorff: positive focused runner-backed probe, not release by itself.

## 2-AI Status-Gate Result

Codex + Bernoulli consensus:

```text
verdict: accept_m14_need_third_strict_probe
release_authorized: false
public_speedup_claim_authorized: false
all_app_pod_spend_authorized: false
focused_pod_spend_authorized_now: false
Barnes-Hut_material_runtime_trunk_Set_A: true, narrowly
RTNN_material_runtime_trunk_Set_A: true
Hausdorff_material_runtime_trunk_Set_A: false
```

Consensus path:
`docs/reviews/codex_bernoulli_phoenix_v3_m14_runtime_trunk_retarget_2ai_consensus_2026-06-22.md`

Hausdorff remains positive focused evidence, but it is not a strict third
material Set-A probe because runner-vs-legacy gains are small.

## Next Controlled Work

M15 should be local and review-gated:

1. Audit Triangle and any alternative Set-A candidates for a real reusable
   runtime-trunk performance source.
2. Choose the best third strict Set-A probe by written criteria.
3. Produce call-for-review before any POD.
4. Only after 2-AI approval should a focused POD A/B be run.

No new POD is authorized by M14.

## Goal-Level Decision Audit

Decision: do not run new POD after M13; reconcile the current runtime-trunk
evidence and seek a status-gate review first.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   The foolish action would be to ignore already-recorded RTNN/Barnes-Hut/
   Hausdorff evidence, repeat old Spatial/RayJoin work, or jump to all-app POD
   before the status gate is updated.
3. Was there another path?
   Yes: run all-app immediately. That would again mix stale scorecard rows and
   create pressure to rationalize a blended number.
4. Can I now try a different path?
   Yes: use this current probe ledger, get 2-AI review on the gate state, and
   only then choose all-app protocol preparation or a third focused Set-A probe.

## Non-Authorization

This report authorizes no V3 release, no public speedup claim, no broad
V3-over-V2 claim, no true-zero-copy claim, no V4/embedding work, and no POD
spend.
