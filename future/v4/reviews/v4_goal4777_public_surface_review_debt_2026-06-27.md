# V4 Goal4777 Public-Surface Review Debt

Date: 2026-06-27

Status: `external_review_closed_by_antigravity_rollup__public_surface_approved`

## Scope

Goal4777 aligns the live public surface with the already published `v4.0.0`
tag while preserving bounded claim wording. It is documented in:

- `future/v4/v4_goal4777_public_surface_main_release_audit_2026-06-27.md`
- `future/v4/reviews/call_for_review_v4_goal4777_public_surface_main_release_audit_2026-06-27.md`

## Original External Review Attempt

Antigravity CLI was available at:

```text
C:\Users\Lestat\AppData\Local\agy\bin\agy.exe
```

The review command was launched in print mode with the Goal4777 call-for-review
packet and the workspace added as a read target. The process produced no output
for more than three minutes and was stopped to avoid blocking release-hardening
work on an empty wait.

Result:

```text
antigravity_review_result: no_output
original_external_review_debt_at_attempt_time: open
current_external_review_debt: closed_by_antigravity_rollup
```

## Closure Update - 2026-06-27

The later consolidated Gemini/external review-debt rollup was reviewed by
Antigravity and closes this Goal4777 public-surface debt.

Reviewed rollup:

- `future/v4/reviews/v4_gemini_review_debt_rollup_for_antigravity_2026-06-27.md`

Antigravity result:

- `future/v4/reviews/antigravity_v4_gemini_review_debt_rollup_2026-06-27.md`

Verdict:

```text
approve_current_external_debt_closed_except_specific_claim_blocks
```

Antigravity explicitly approved the two active P0 items:

- the public documentation fix response after the earlier documentation block;
- the Goal4777 public-surface release audit.

It also confirmed that the Gemini review debt seat remains closed for the
bounded V4.0 tag and that Barnes-Hut/paper-reproduction issues remain
specific-claim blockers only, not V4.0 public-tag blockers.

## Local Gate Status

Public examples:

```text
all public examples passed
```

Focused public-surface/release-gate tests:

```text
Ran 23 tests in 30.537s
OK
```

Full V4 local discovery:

```text
Ran 645 tests in 92.488s
OK (skipped=1)
```

## Debt Handling

This debt is closed for the bounded V4.0 public tag. It does not expand the
release scope or authorize any additional claims.

## Non-Authorization

This debt does not authorize:

- broad all-app speedup wording;
- broad V4-over-V2.14 or V4-over-V3 speedup wording;
- whole-application high-performance release wording;
- Tier-3 callback/PTX public support;
- raw OptiX callback support;
- public true-zero-copy claims;
- embedding/C ABI/non-Python host claims;
- public paper-reproduction speedup claims;
- moving or force-updating the already pushed `v4.0.0` tag.
