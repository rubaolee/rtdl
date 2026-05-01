# Goal1083 Formal Review

Date: 2026-04-29
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

---

## Scope

This review covers Goal1083 only: the addition of the
`facility_service_coverage_recentered` scenario to the Goal887 profiler and its
local 2.5M-copy CPU oracle artifact. It does not re-review Goal887, Goal1082,
or any RTX cloud run.

---

## Check 1 — Recentered scenario addresses the large-coordinate precision problem

**PASS.**

Goal1082 identified the root cause: at 2,500,000 copies the original facility
x-coordinates reach approximately 15,000,000 while the service radius is 1.0,
making float-precision RT traversal unsafe. Goal1083 adds
`_recenter_facility_points` (script line 233–241), which subtracts
`(int(point.id) // 100) * 6` from each customer's x coordinate, bringing every
query point back into copy-local range. The canonical depot build set is drawn
from `copies=1` only (`_canonical_facility_depots`, line 244–245), so queries
and build points share the same local coordinate frame.

The unit test `test_facility_recentered_keeps_large_copy_coordinates_local`
(test line 103–111) directly validates this: with 1,000 copies the original max
x exceeds 5,000 and the recentered max x falls below 4.0. The claim is
well-founded and testable.

---

## Check 2 — Claim scope is honest; excludes global-coordinate identity, KNN, and whole-app claims

**PASS.**

The `_cloud_claim_contract` for `facility_service_coverage_recentered` (script
lines 63–65) explicitly states:

- `claim_scope`: "prepared OptiX fixed-radius threshold traversal for recentered
  facility service-coverage decisions"
- `non_claim`: "not ranked nearest-depot assignment, KNN fallback assignment,
  facility-location optimization, or global-coordinate identity matching"

The phrase "global-coordinate identity matching" is the new addition relative to
the non-recentered variant and directly names the precision hazard that triggered
Goal1082. The profiler-level `boundary` string (script line 483–487) reaffirms
no RTX speedup claim is authorized without a real RTX run, same-semantics
baselines, and independent review. The MD boundary section (report line 69–72)
repeats this. Scope discipline is sound.

---

## Check 3 — Local 2.5M dry-run artifact is valid

**PASS.**

The artifact `goal1083_facility_recentered_2_5m_cpu_oracle.json` is consistent
and internally coherent:

| Field | Value | Assessment |
|---|---|---|
| `schema_version` | `goal887_prepared_decision_phase_contract_v1` | Correct |
| `mode` | `dry-run` | CPU oracle only; no RTX hardware claim |
| `copies` | `2,500,000` | Matches the blocked same-scale size |
| `customer_count` | `10,000,000` | Correct (4 customers × 2.5M copies) |
| `covered_customer_count` | `10,000,000` | All covered |
| `all_customers_covered` | `true` | Oracle confirms correctness |
| `coordinate_mapping` | `copy_local_recentered_queries_canonical_depots` | Explicitly recorded |
| `skip_validation` | `false` | Validation was not skipped |
| `activation_status` | `deferred_until_real_rtx_phase_run_and_review` | Correctly deferred |

The CPU oracle runtime of 8.3 s is plausible for a coverage scan over 10M
points. The `input_build_sec` of 109 s reflects the cost of constructing 2.5M
copies and is expected. The 10M/10M coverage result demonstrates the recentered
mapping is semantically faithful to the original coverage question.

---

## Check 4 — Next cloud command correctly omits --skip-validation

**PASS.**

The next cloud command (report lines 53–61) does not include `--skip-validation`.
The report is explicit (line 63–65): "Do not use `--skip-validation` for this
run. If validation is too expensive on the pod, stop and add a reviewed
validation-equivalent artifact instead of publishing a speedup ratio."

This directly addresses the specific failure mode of Goal1082: the blocked RTX
timing row had `skip_validation: true`, which meant the semantic mismatch (8.9M
vs 10M covered) went undetected until the same-scale CPU oracle was run
separately. The instruction is clear and conservative.

---

## Check 5 — No public RTX speedup claim or release/public wording change authorized

**PASS.**

No RTX timing data exists for the recentered scenario. The artifact is a dry-run
CPU oracle only. `activation_status` is `deferred_until_real_rtx_phase_run_and_review`.
The MD boundary section (lines 69–72) states explicitly: "It does not authorize
public RTX speedup wording, does not change release status, and does not claim
whole-app facility KNN acceleration." The `facility_service_coverage_recentered`
scenario is absent from the active manifest entries tested in
`test_manifest_uses_phase_profiler_for_new_prepared_decision_entries` (test
lines 60–84), confirming it has not been promoted into any cloud run batch.

---

## Summary

All five checks pass. Goal1083 is a disciplined engineering response to the
Goal1082 BLOCK verdict. It identifies the root cause (large-coordinate float
precision), implements a correct recentering mapping, validates it with a CPU
oracle at the full 2.5M-copy scale, explicitly records the coordinate mapping in
the artifact, narrows the non-claim to exclude global-coordinate identity
matching, and requires validation on the next cloud run. No public claim or
release action is taken.

**Verdict: ACCEPT**

The recentered scenario and its local artifact are approved as a prerequisite
for the next RTX cloud run. A cloud run producing a real RTX timing artifact
with validation passing remains required before any public RTX speedup claim for
the facility scenario is authorized.
