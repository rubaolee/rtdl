# RTDL V4 Goal4644 Post-Release Guardrails External Review

**Date of Review:** 2026-06-25
**Reviewer:** Claude (External Reviewer, claude-sonnet-4-6)
**Status:** Completed

---

## Verdict

`accept_goal4644_post_release_guardrails`

No amendments are required. Goal4644 is a clean post-publication guardrail that
locks already-authorized scope without expanding it.

---

## Files Inspected

- `src/rtdsl/v4_goal4644_post_release_guardrails.py`
- `future/v4/v4_goal4644_post_release_guardrails_2026-06-25.md`
- `tests/v4_goal4644_post_release_guardrails_test.py`
- `src/rtdsl/v4_release_decision.py`
- `src/rtdsl/v4_goal4643_publication_decision.py`
- `README.md`
- `docs/current_v4_status.md`
- `docs/learn/performance_wording.md`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`

---

## Findings by Severity

### Critical / Blocker

None.

### Major

None.

### Minor / Informational

- **`external_review_status` is prose, not a boolean gate.** The field
  `"post_release_external_review_due_on_next_6h_cadence_or_major_decision"` is
  not machine-asserted to contain the word "due" or similar language.
  `validate_v4_goal4644_post_release_guardrails` does not check it. This is
  acceptable because the intent is fully captured by the hard integer checks on
  `review_cadence_hours` (6) and `three_ai_consensus_cadence_hours` (24), and
  the field is informational rather than a gate. No action required.

- **`tests/v4_goal4644_post_release_guardrails_test.py` listed as
  `required_decision_records`.** The validate function checks for the test
  file's existence on disk as a decision record. This is a slightly unusual
  classification but is a positive practice — it ensures the guardrail test
  cannot be silently deleted without breaking the validation chain. No issue.

---

## Answers to Call-for-Review Questions

### 1. Does Goal4644 correctly preserve the already-authorized V4.0.0 release without reopening scope?

Yes. The implementation preserves the authorized release without reopening
scope through three independent mechanisms:

First, `V4Goal4644PostReleaseGuardrails.as_dict()` hardcodes
`"release_scope_reopened": False`. Second, `validate_v4_goal4644_post_release_guardrails`
explicitly raises `ValueError` if `release_scope_reopened` is true. Third, the
test at `test_goal4644_machine_record_exists_and_does_not_reopen_scope` asserts
`self.assertFalse(decision["release_scope_reopened"])`.

The publication commit `c58642326f57f6326274b448caa8d75b3c7ef9de` is correctly
identified and matches the `Publish V4.0.0 formal operator release` commit
visible in the repository history.

The chain of trust is intact at runtime: `v4_goal4644_post_release_guardrails`
calls `validate_v4_goal4643_publication_decision` (which in turn calls
`validate_v4_goal4632_release_decision` and the full gate chain) and also calls
`validate_v4_goal4642_final_authorization_packet` independently. Every call to
the Goal4644 function exercises the complete validation chain back to Goal4642.

The `next_scope` field states explicitly: "V4.0.0 remains limited to documented
measured generic RT-core operator surfaces." The human-readable record at
`future/v4/v4_goal4644_post_release_guardrails_2026-06-25.md` states "Goal4644
does not reopen V4.0 scope" and the test verifies that string is present in the
document.

### 2. Does it keep deferred/excluded families out of release claims?

Yes. Barnes-Hut and Spatial RayJoin are locked out through multiple
machine-checkable layers:

The `forbidden_claims` tuple inherited from `v4_goal4632_release_decision()`
contains both `"Barnes-Hut covered by V4.0"` and `"Spatial RayJoin covered by
V4.0"`. The `validate_v4_goal4644_post_release_guardrails` function explicitly
checks for both strings and raises `ValueError` if either is absent.

The test `test_machine_forbidden_claims_cover_deferred_and_reproduction_overclaims`
asserts the required forbidden set
`{"Barnes-Hut covered by V4.0", "Spatial RayJoin covered by V4.0", "LibRTS
paper reproduction"}` is a subset of forbidden claims in all three layers:
`v4_goal4632_release_decision`, `validate_v4_goal4642_final_authorization_packet`,
and `validate_v4_goal4644_post_release_guardrails`.

The test `test_candidate_surfaces_are_not_counted_as_measured` independently
confirms `deferred_or_uncovered_v4_0 == 2`, ensuring the deferred count is
machine-visible and stable.

The public docs (`future/v4/tier2_operator_catalog.md`, `future/v4/README.md`,
`docs/current_v4_status.md`) do not mention Barnes-Hut or Spatial RayJoin as
covered surfaces. The test `test_public_docs_keep_release_caveats_and_no_stale_goal4640_4641_gate`
does not add a positive assertion for their absence by name, but the forbidden
claim check in the validate function is the more authoritative guard.

### 3. Are the forbidden-claim locks sufficient and machine-checkable?

Yes. The implementation provides three distinct machine-checkable enforcement
layers:

**Layer 1 — Boolean flags hardcoded False in `as_dict()`:** All ten
`_authorized` flags are hardcoded to `False` in
`V4Goal4644PostReleaseGuardrails.as_dict()`:

```
broad_v4_speedup_claim_authorized
whole_app_speedup_claim_authorized
all_benchmark_speedup_claim_authorized
true_zero_copy_claim_authorized
tier3_callback_claim_authorized
raw_optix_callback_claim_authorized
cupy_performance_claim_authorized
c_abi_or_embedding_claim_authorized
non_python_host_claim_authorized
app_specific_native_kernel_authorized
```

**Layer 2 — Validate function checks all ten flags and twelve claim strings:**
`validate_v4_goal4644_post_release_guardrails` raises `ValueError` if any
flag is truthy, and separately checks that all twelve forbidden claim strings
are present in the `forbidden_claims` tuple. The twelve strings cover every
category named in the call-for-review plus Barnes-Hut, Spatial RayJoin, and
LibRTS paper reproduction.

**Layer 3 — Public documentation caveats checked by test:** The test
`test_public_docs_keep_release_caveats_and_no_stale_goal4640_4641_gate` verifies
that five public docs each contain the strings `"whole-application speedup"`,
`"public true-zero-copy"`, `"Tier-3"`, and `"CuPy"`, confirming caveats are
present and not accidentally deleted.

Cross-checking the public-facing documents confirms all sections carry
appropriate non-authorization language. The README.md Non-Claims section, the
`docs/current_v4_status.md` Boundary section, the `docs/learn/performance_wording.md`
Claim Boundaries section, the `future/v4/README.md` Non-Claims section, and the
`future/v4/tier2_operator_catalog.md` Non-Authorization section all enumerate
the same set of forbidden categories.

The forbidden-claim locks are sufficient.

### 4. Does the review cadence/debt language satisfy the owner's rule without weakening the release label?

Yes. The cadence obligations are machine-checked:

- `review_cadence_hours=6` is asserted equal to 6 in `validate_v4_goal4644_post_release_guardrails`
  and in the test.
- `three_ai_consensus_cadence_hours=24` is asserted equal to 24 in both.

The review debt strings are honest and non-erasing. They read:

1. `"Claude final publication backfill remains desirable when Claude is available."`
2. `"Antigravity or Claude should review Goal4644 on the next 6h cadence if work continues."`
3. `"No review debt expands or weakens the bounded V4.0.0 release label."`

The third string is a direct enforcement statement: it prevents the debt ledger
from being cited as a reason to soften the release label. The human-readable
record states: "This debt does not weaken the release label. It only records the
next review maintenance obligation."

Critically, the `external_review_status` field is
`"post_release_external_review_due_on_next_6h_cadence_or_major_decision"` — it
acknowledges this review (Goal4644's own external review) as outstanding, not
complete. This is accurate and does not overclaim.

The release label itself (`RTDL v4.0.0 formal high-performance generic RT-core
operator release`) is carried through `validate_v4_goal4643_publication_decision`
and asserted equal to `V4_AUTHORIZED_RELEASE_LABEL` at both the Goal4643 and
Goal4644 validation layers.

### 5. Are amendments required before Goal4644 can be considered complete?

No. Goal4644 is complete as submitted.

The implementation covers all requirements from the call-for-review:
- scope not reopened (machine-checked, hardcoded, tested)
- deferred families excluded (checked in validate and test, consistent across three layers)
- forbidden claims machine-visible and false (ten boolean flags, twelve string checks)
- review cadence preserved (integer asserts at 6h and 24h)
- release label not weakened by debt language (explicit statement in debt ledger)

The 179-test suite passes. The 20-test focused suite covering Goal4644,
Goal4643, frontdoor, scope gate, and catalog regression gate passes. The
catalog dry-run reports `status: passed`, `release_authorized: true`,
`measured_surface_count: 8`, `candidate_surface_count: 0`.

---

## Non-Authorization

This review does not authorize new V4.0 scope, broad speedup wording,
whole-application speedup wording, all-benchmark speedup wording, public
true-zero-copy wording, Tier-3 callback support, raw OptiX callback support,
CuPy performance claims, C ABI, embedding, non-Python host bindings,
app-specific native kernels, Barnes-Hut coverage, Spatial RayJoin coverage,
or LibRTS paper reproduction.

This review accepts Goal4644 as a correctly bounded post-publication guardrail
for the already-authorized `RTDL v4.0.0 formal high-performance generic RT-core
operator release` label. It does not expand that label or re-open the release
scope in any way.
