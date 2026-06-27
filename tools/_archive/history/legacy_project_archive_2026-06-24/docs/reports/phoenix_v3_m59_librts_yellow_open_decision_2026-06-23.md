# Phoenix V3 M59 LibRTS Yellow/Open Decision

Date: 2026-06-23

Status:

```text
m59_librts_set_b_yellow_open_limit_not_step2_gap_pending_external_review
```

## Scope

M59 decides what to do after M58 accepted the single M57-authorized LibRTS
rerun as valid evidence intake, while leaving both LibRTS rows yellow/open.

This is a decision and review packet only. It does not run POD, close watch
rows, authorize all-app benchmarking, or authorize V3 release.

Primary inputs:

- `docs/reports/phoenix_v3_m58_librts_m57_authorized_pod_rerun_intake_2026-06-23.md`
- `docs/reviews/codex_claude_antigravity_phoenix_v3_m58_rerun_intake_3ai_consensus_2026-06-23.md`
- `docs/reviews/phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md`
- `docs/rebuild/v3/proposed_v3_redesign_build_the_runtime_trunk_first_2026-06-22.md`
- `docs/rebuild/v3/evidence/phoenix_v3_m58_librts_m57_authorized_execution_20260624_0055/summary.json`

## Decision

LibRTS/AABB should be carried forward as a **Set-B yellow/open control
limitation**, not treated as a new Step-2 runtime optimization gap.

Machine-readable classification phrase:

```text
Set-B yellow/open control limitation
```

That means:

- do not spend the next runtime-engine cycle tuning LibRTS/AABB;
- do not run another focused LibRTS POD job from M59;
- keep both LibRTS rows open in the release evidence ledger;
- require user-language explanation for the OptiX cold single-shot weakness;
- return Step 2 work to Set-A runtime families where residency and continuation
  can compound.

## Why This Is The Correct Classification

The Set-A/Set-B scorecard defines Set A as architecture-bearing probes:
multi-phase, residency-rich, continuation-heavy workloads where the prepared
runner can produce a material runtime-sourced gain.

LibRTS/AABB in the M47/M58 evidence is not that. It is a prepared AABB index
count/query-set control route. The local source and M58 payload both classify
the route as:

```text
set_a_probe_candidate=false
set_b_control_candidate=true
```

That makes it a control row. Its job is to show that the V3 runner does not
tax single-shot or backend-ceiling routes beyond an explainable parity band.
It is not the place where V3 earns the 1.20x Set-A major-version performance
claim.

## M58 Evidence Read

| Scenario | Label | Geomean | Median | Min | Max | Pass count >=0.95 | First-sample-stripped geomean | M59 read |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `embree_32768_stress` | `yellow_stability_boundary_watch_row_open` | 1.030501x | 1.022440x | 0.870986x | 1.225962x | 6/8 | 1.055558x | parity-positive but noisy |
| `optix_cold_single_shot` | `yellow_stability_boundary_watch_row_open` | 0.979485x | 0.938318x | 0.833096x | 1.210241x | 3/8 | 1.002400x | near-parity by geomean after first sample, but weak and open |

The metadata issue from M55 is cleared:

```text
set_b_control_candidate_missing: cleared
```

The timing issue is not cleared. The OptiX cold single-shot row remains weak:

- its full geomean is just under the Set-B `0.98x` parity line;
- its median is under `0.95x`;
- only 3 of 8 samples clear `0.95x`;
- stripping the first sample brings geomean to parity, which points toward
  cold/single-shot variability, but this is explanation, not closure.

## What This Means For Phoenix Step 2

Step 2 asks whether the same productized runner can serve additional Set-A
families without becoming another app-specific route. LibRTS/AABB does not
answer that question because it is a Set-B control row.

So M59 should unblock the trunk work by saying:

```text
LibRTS remains yellow/open, but it is not the next Step-2 trunk family.
```

The next Step-2 work should target a Set-A family such as Spatial/RayJoin,
RTNN/ranked summary, RT-DBSCAN/component continuation, Barnes-Hut/frontier
accumulation, Triangle, or Hausdorff threshold summary, with the same rule:
wins must come from the productized runtime path, not a route-specific cache.

## Release Impact

This decision does not make LibRTS green.

For a future release decision:

- LibRTS can remain a Set-B control only if the final evidence packet carries
  the yellow/open explanation honestly.
- Any final Set-B scorecard must still meet the reviewed parity rule or carry
  accepted row-level explanation.
- If later all-app evidence shows the V3 execution path adds systematic
  overhead to Set-B controls, LibRTS becomes a runtime overhead bug.
- M59 does not authorize broad V3-over-V2 performance wording.

## Next Allowed Action

Pending external review, the recommended next action is:

```text
continue Step 2 on the next Set-A runtime family; do not rerun or optimize
LibRTS from M59.
```

M60 should therefore be a reviewed Step-2 Set-A selection packet, not another
LibRTS stability run.

## Non-Authorization

This report does not authorize:

- no V3 release
- no all-app benchmark run
- no broad paid POD campaign
- no second M57 run
- no additional LibRTS POD run
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true-zero-copy claim
- no watch-row closure

## Goal-Level Decision Audit

Decision: classify M58 LibRTS as Set-B yellow/open limitation, not the next
Step-2 runtime optimization gap.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish action would be
   chasing a single-shot Set-B control row as though it were the main V3
   performance trunk, or calling it green because metadata was fixed.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Respect the frozen Set-A/Set-B split, preserve the yellow/open label,
   and spend engineering cycles where the runtime can actually compound.
4. Can I now try a different path that actually solves the problem? Yes. Return
   Step 2 to Set-A runtime families and keep LibRTS as an explained control-row
   risk for the eventual scorecard.
