# Recorded External Review: Claude Phoenix V3 M30-M34 Bundle

Date: 2026-06-23

Reviewer: Claude

Status: `external_verdict_obtained_claude_accept_m30_m33_continue_trunk_first_not_release`

Raw capture:

- `docs/reviews/claude_phoenix_v3_m30_m33_bundle_review_2026-06-23.raw.md`
- stderr: `scratch/claude_phoenix_v3_m30_m33_bundle_review_2026-06-23.err.txt`
- scheduled runner log:
  `scratch/claude_phoenix_v3_m30_m33_bundle_scheduled_runner_2026-06-23.log`

## Verdict

```text
verdict: accept_m30_m33_continue_trunk_first
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
v4_work_authorized: false
```

Claude also accepted the M34 local addendum:

```text
M34 verdict: correction is valid
M34 finding: run_fixed_radius_threshold_reached_count_2d_prepared_session was a genuine __all__ drift
M34 result: surface ledger gate now enforces 11 = 11
```

## Accepted Milestones

- M30: `accept_m30_rtnn_as_second_set_a`
- M31: `accept_m31_shared_audit_surface`
- M32: `accept_m32_continuation_core_audit_surface`
- M33: `accept_m33_step4_promotion_ledger`
- M34: surface-ledger correction valid

## Required Carry-Forward Clarification

Claude's non-blocking but required clarification:

`Step-4 ready by local audit` means the metadata structure passes the M31/M32
gate. It does not mean measured material performance gains exist for all seven
families. In particular, RTDBSCAN component-signature and RayJoin
point-location have parity or not-material prior POD results. Future summaries
must preserve this distinction.

## Next Work Authorized By This Review

Authorized:

- continue non-all-app trunk hardening;
- use the M31/M32 ledger to identify which remaining families need focused POD
  evidence before any later all-app consideration;
- continue promoting reusable continuation families such as grouped reduction
  and component union into runner-callable core nodes where they still remain
  app-mode route code;
- extend M31 audit wiring to any future prepared-session families added after
  M33.

Not authorized:

- Phoenix V3 release;
- any all-app paired POD run;
- public speedup claims;
- broad V3-over-V2.x speedup wording;
- true-zero-copy wording;
- automatic backend or partner selection;
- V4 work, C ABI work, embedding work, or external-buffer wording;
- reversal of the M22 all-app non-release result.

## Goal-Level Decision Audit

Decision: accept Claude's external review as the external-AI half of the
M30-M34 trunk-first consensus, while keeping release/all-app/public-claim gates
closed.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   The foolish action would be treating the accepted M30-M34 review as release
   authorization or all-app POD authorization. This record explicitly refuses
   that.

3. Was there another path?

   Yes: keep waiting, use Gemini despite authentication failure, or treat Codex
   self-review as enough. Those paths would either stall or violate the user's
   external-review rule.

4. Can I now try a different path that actually solves the problem?

   Yes. Use the accepted external review to proceed with bounded non-all-app
   trunk hardening, starting from the two weak Step-4-ready families Claude
   named: RTDBSCAN component-signature and RayJoin point-location.
