# Codex + Claude 2-AI Consensus: Phoenix V3 M22 All-App POD Result

Date: 2026-06-23

## Inputs

- Codex result report:
  `docs/reports/phoenix_v3_m22_all_app_pod_result_2026-06-23.md`
- Paired evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315/summary.md`
- Protocol gate:
  `docs/rebuild/v3/evidence/phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315/m21_protocol_gate.md`
- Claude facts-only review request:
  `docs/reviews/call_for_review_phoenix_v3_m22_all_app_result_facts_only_2026-06-23.md`
- Claude raw review:
  `docs/reviews/claude_phoenix_v3_m22_all_app_result_review_2026-06-23.raw.md`

Note: an initial file-reading Claude invocation was stopped after it remained
silent with zero-byte output. The successful Claude review used a facts-only
prompt containing the extracted run facts, gate status, app geomeans, row-level
failures, and Codex conclusion.

## Shared Verdict

Verdict: `approve_blocked_not_release`

Codex and Claude agree that the M22 all-app POD run is serious engineering
evidence, but it does not authorize Phoenix V3 release as a performance-major
version. It also does not authorize public speedup claims or broad "V3 is faster
than V2.x" claims.

## Controlling Facts

```text
same_metric_comparison_count: 51
primary_metric_source_mismatch_count: 0
overall_geomean_v3_speedup_vs_v2_14: 1.049x
set_a_geomean_v3_speedup_vs_v2_14: 1.013x
set_b_geomean_v3_speedup_vs_v2_14: 1.210x
apps_above_1_05x: 4_of_10
barnes_hut_app_geomean: 0.831x
m21_protocol_gate_status: protocol_fail_invalid_or_out_of_scope
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

## Consensus Findings

1. The run is structurally useful evidence, but the protocol gate fails.
   Suite-driver `rc=0` does not override row-level correctness failures.

2. Phoenix V3 has at least one current-code correctness defect:
   `rayjoin_optix_promoted_overlay_seed_tiled_x2048` fails with an unexpected
   `point_order_mode` argument. Claude ranks this as the first fix because a
   V3 code defect can invalidate nearby timing interpretation.

3. Barnes-Hut is a release-blocking severe regression. Its app geomean is
   0.831x, below both the app geomean floor and the severe-regression floor.

4. The overall geomean of 1.049x is far below the preregistered 1.20x bar.
   Only 4 of 10 app geomeans exceed 1.05x, below the required 8 of 10.

5. Set-A is nearly flat at 1.013x. This is the central Phoenix V3 architecture
   concern because Set-A is where execution/residency trunk gains should appear.
   Set-B at 1.210x cannot substitute for the missing Set-A runtime effect.

6. LibRTS AABB OptiX index is a live watch-row regression at 0.803x, even
   though the app geomean is strong. It must be isolated rather than hidden by
   the app-level win.

7. V2.14 baseline failures on Spatial RayJoin and Triangle Counting are
   confounding rows. They must be fixed, excluded with justification, or clearly
   marked as unverified before those comparisons are used.

## Required Next Actions Before Another All-App Run

1. Fix the Phoenix V3 RayJoin OptiX `point_order_mode` defect and verify the row
   completes with correct output.

2. Diagnose and repair Barnes-Hut, especially the OptiX node-coverage path.
   Focused Barnes-Hut probes must clear at least the 0.900x regression floor
   before another all-app run is justified.

3. Trace the LibRTS OptiX AABB index watch row in isolation and either fix it or
   document a rigorous exclusion.

4. Run focused Set-A execution/residency probes to prove the shared Phoenix V3
   trunk is producing runtime-sourced gains. Do not rely on Set-B wins to claim
   the V3 architecture is working.

5. Repair or formally exclude V2.14 baseline failures before using those rows in
   comparative claims.

6. Do not spend another all-app POD cycle until the above blockers are closed.

## Non-Authorization

Release is not authorized.

Public speedup claims are not authorized.

Broad comparative claims such as "Phoenix V3 is faster than V2.x" are not
authorized.

These restrictions remain until a future run passes the protocol gate with clean
row-level correctness, overall geomean >= 1.20x, at least 8 of 10 app geomeans
above 1.05x, and no severe app regression.

## Goal-Level Decision Audit

1. Was I foolish?

No for the consensus decision. The decision accepts the failed gate and Claude's
blocking review instead of trying to promote selective wins.

2. If yes, what actions made the decision foolish?

No new foolish action is recorded for the consensus decision. The risky pattern
would have been to treat a facts-only review as release authorization; this file
does the opposite and records non-authorization.

3. Was there another path?

Yes. I could have waited indefinitely for the file-reading Claude invocation, or
ignored Claude and closed with Codex-only judgment. The first would waste time;
the second would violate the 2-AI consensus rule for important results.

4. Can I now try a different path?

Yes. The different path is evidence-first repair: fix correctness, Barnes-Hut,
LibRTS watch row, and Set-A trunk proof before another all-app run.
