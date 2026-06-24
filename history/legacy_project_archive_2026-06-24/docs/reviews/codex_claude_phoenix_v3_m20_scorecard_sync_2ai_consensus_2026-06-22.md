# Codex + Claude 2-AI Consensus: Phoenix V3 M20 Scorecard Sync

Date: 2026-06-22

Status: `authorize_m20_all_app_protocol_preparation_no_run`

## Verdict

Codex accepts Claude's external verdict:

```text
authorize_m20_all_app_protocol_preparation_no_run
```

This authorizes preparing a strict all-app POD protocol packet only. It does
not authorize running all-app POD.

## External Review

```text
review: docs/reviews/claude_phoenix_v3_m20_scorecard_sync_after_triangle_review_2026-06-22.md
verdict: authorize_m20_all_app_protocol_preparation_no_run
```

Claude confirmed:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_run_authorized_now: false
all_app_pod_protocol_preparation_authorized_now: true
triangle_remains_closed_as_third_strict_set_a_probe: true
```

## Required Protocol Content

The M20 all-app POD protocol packet must include:

```text
1. Pre-registered per-metric fail-closed bars:
   - Barnes-Hut app geomean < 0.90x => protocol FAIL
   - librts_embree_aabb_index < 0.95x => protocol FAIL
   - Set-B geomean < 0.98x => protocol FAIL
   - any new app-level severe regression below 0.90x => protocol FAIL
   - Set-A geomean and Set-A apps over 1.05x reported exactly, not used as pass/fail for this evidence run

2. Explicit non-release declaration in the protocol header.

3. Frozen case-ID whitelist preserved.

4. Same hardware requirement:
   NVIDIA RTX 4000 Ada Generation, driver 550.127.05, compute capability 8.9.

5. Project venv requirement and subprocess interpreter pre-launch check:
   /root/rtdl_v3_rebuild_20260620/.venv/bin/python or equivalent verified path.

6. LibRTS OptiX AABB watch-row disclosure.

7. Oracle/correctness checks for all apps before accepting performance rows.

8. Post-run result handling:
   - if both blocking bars clear, record blocking bars cleared and update scorecard baseline, release still not authorized;
   - if either fails, protocol fails and further local/focused work is required before another all-app run.
```

## Non-Authorization

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_run_authorized_now: false
release_based_on_all_app_run_outcome: false
m19_citable_as_broad_v3_performance: false
```

## Goal-Level Decision Audit

Decision: proceed to M21 protocol preparation but do not run all-app POD.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   It would be foolish to treat protocol preparation authorization as run or
   release authorization. This consensus explicitly forbids that.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Keep doing focused fixes without a transfer test. Claude judged that
   as delay because the focused fixes already exist and only an all-app run can
   test transfer.
4. Can I now try a different path that actually solves the problem?
   Yes. Prepare the all-app protocol packet with fail-closed bars and submit it
   for another external 2-AI authorization before spending POD.
