# Phoenix V3 M20 Scorecard Sync After Triangle M19

Date: 2026-06-22

Status: `scorecard_synced_triangle_probe_closed_protocol_preparation_authorized_no_run`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
all_app_pod_protocol_preparation_authorized: true
```

## Bottom Line

M19 closes Triangle as the third strict Set-A material runtime-trunk probe.
The Set-A/Set-B scorecard now records:

```text
focused_productized_material_probe_count_verified: 3
required_focused_productized_material_probe_count_before_full_all_app_pod_run: 2
missing_focused_productized_material_probe_count: 0
```

This improves the runtime-trunk evidence base, but it still does not authorize
all-app POD or release. The current frozen all-app scorecard remains blocked by
the old serious paired run:

```text
Set A geomean: 1.013x
Set A apps over 1.05x: 1 / 5 required
Set A severe regression apps: barnes_hut=0.844x
Set B rows below 0.95x: librts_spatial_index embree AABB=0.869x
all_app_pod_spend_authorized: false
release_candidate_under_two_number_bar: false
```

## Files Updated

```text
docs/rebuild/v3/phoenix_v3_set_a_set_b_classification_2026-06-22.json
docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.json
docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md
docs/handoff/PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md
tests/v3_phoenix_set_ab_scorecard_gate_test.py
```

## Probe Ledger

```text
1. aabb_runner_m2_1
   classification: material_focused_productized_path_probe_not_release

2. hausdorff_threshold_runner_m5_after_m6_1
   classification: positive_focused_productized_runner_backed_probe_not_release

3. triangle_m19_env_corrected_productized_runner
   classification: accepted_third_strict_set_a_material_probe_not_release
```

## Interpretation

The missing-probe precondition is now closed with margin (`3/2`). The remaining
blocker is no longer "we need a third focused material probe." The remaining
blocker is whether the current code has accumulated enough broad reusable
runtime fixes to justify a new serious all-app POD run despite the old frozen
scorecard still showing Set-A and Set-B blockers.

Claude's M20 review authorized all-app POD protocol preparation only:

```text
docs/reviews/claude_phoenix_v3_m20_scorecard_sync_after_triangle_review_2026-06-22.md
verdict: authorize_m20_all_app_protocol_preparation_no_run
```

Codex + Claude consensus:

```text
docs/reviews/codex_claude_phoenix_v3_m20_scorecard_sync_2ai_consensus_2026-06-22.md
status: authorize_m20_all_app_protocol_preparation_no_run
```

Therefore the next action is to write the all-app POD protocol packet. It must
then receive a separate external 2-AI authorization before any all-app POD run.
No all-app POD run is authorized now.

## Goal-Level Decision Audit

Decision: update the Set-A/Set-B scorecard to 3/2 focused probes after M19 and
accept Claude's authorization to prepare, but not run, an all-app POD protocol.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   It would be foolish to treat 3/2 focused probes as automatic all-app or
   release authorization.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Leave the scorecard at 2/2 and hide the Triangle evidence. That would
   be stale and misleading.
4. Can I now try a different path that actually solves the problem?
   Yes. Record the improved probe ledger, then request a bounded external
   review on the next all-app POD precondition instead of spending POD
   immediately.
