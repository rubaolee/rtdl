# Call For Review: Phoenix V3 Performance Failure Root Cause and Remaining Optimizations

Date: 2026-06-22
Requester: Codex
Scope: Phoenix V3 only. Do not discuss or reopen V4 / C ABI / embedding.

## Document Under Review

`docs/reports/phoenix_v3_performance_failure_root_cause_and_remaining_optimizations_cn_2026-06-22.md`

## Controlling Facts

```text
Phoenix V3 status: redo_required
same-hardware V2.14 vs Phoenix V3 all-app geomean: 1.0117790403434224
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
focused_m3_4_pod_ab_authorized: true
```

## Review Questions

Please review critically and return one of these labels:

```text
approve_record_only_not_release
approve_with_required_edits_not_release
reject_misleading_or_incomplete
blocked_no_substantive_review
```

Answer these questions explicitly:

1. Does the document clearly state that Phoenix V3 currently has no release-level performance proof?
2. Does it list the completed optimizations with enough specificity to support handoff?
3. Does it distinguish material speedup, parity recovery, hygiene cleanup, and row-scoped evidence?
4. Does it explain why each optimization was originally plausible?
5. Does it explain why many optimizations did not actually produce V3-level performance?
6. Are any statements too strong, misleading, or public-claim unsafe?
7. Are the remaining optimization plans generic runtime/language work rather than benchmark-app customization?
8. Are the success/stop rules strong enough to prevent another fake V3 release?

## Required Boundary

Do not authorize:

```text
release
public speedup claim
broad V3 faster than V2 claim
full all-app pod rerun
V4/embedding/C-ABI work
```

If approved, the maximum allowed meaning is:

```text
This is a technical accounting and planning document only.
Phoenix V3 remains redo_required.
```
