# Goal1059 External Review

Reviewer: Claude (Sonnet 4.6)
Date: 2026-04-28

## Verdict: ACCEPT

Goal1059 is truthful, internally consistent, and does exactly what it claims.

---

## What Was Verified

### 1. Old skip-validation blockers are gone

`_RTX_PUBLIC_WORDING_MATRIX` in `src/rtdsl/app_support_matrix.py` now uses two
Goal1058-specific policy constants:

- `_GOAL1058_FACILITY_VALIDATED_POLICY` — "oracle parity. Public speedup wording
  remains blocked until a separate baseline/timing wording review authorizes a
  bounded sub-path claim."
- `_GOAL1058_ROBOT_VALIDATED_POLICY` — "oracle parity. Public speedup wording
  remains blocked because the claim-review path still needs timing-floor/baseline
  review."

Neither entry references Goal1048 skip-validation runs as the active blocker.
Both correctly credit Goal1058 as the current evidence anchor.

### 2. Public speedup wording remains blocked / unauthorized

Both `facility_knn_assignment` and `robot_collision_screening` stay at
`PUBLIC_WORDING_BLOCKED` with `evidence = "Goal1058"`. No speedup ratio, no
baseline comparison, no whole-app claim was introduced anywhere in the diff.

### 3. Docs propagation is consistent

| Document | Key assertions verified |
| --- | --- |
| `README.md` (RT-Core Claim Boundary) | Lines 97–106 correctly state robot is excluded due to timing floor, Goal1058 validated pose-flag oracle parity. Lines 103–106 correctly state facility excluded after Goal1058, oracle parity validated, no speedup claim authorized. `goal1058_three_ai_same_semantics_consensus_2026-04-28.md` is linked. |
| `docs/v1_0_rtx_app_status.md` | Summary records `post-Goal1048 validated RTX artifact intake completed (Goal1058): True`, `reviewed_public_wording = 6`, `public_speedup_claim_authorized: False`. Both apps show `blocked_for_public_speedup_wording` with Goal1058 oracle parity language. |
| `docs/app_engine_support_matrix.md` | Cloud benchmark policy paragraph cites both Goal1048 commit hash and Goal1058; `blocked_for_public_speedup_wording` is present; `Goal1008 keeps public speedup wording blocked` and `Goal1058 validated oracle` both appear. |
| `docs/reports/goal1051_post_goal1048_followup_plan_2026-04-28.md` | `diagnostic_reruns` rows for facility and robot now cite Goal1058 oracle-parity policy rather than skip-validation language. |
| `docs/reports/goal947_v1_rtx_app_status_2026-04-25.json` | `facility_knn_assignment.cloud_action` contains "Goal1058 RTX A5000 diagnostic rerun validated facility coverage with oracle parity." `public_wording_status = "public_wording_blocked"` for both apps. |
| `docs/reports/goal1058_three_ai_same_semantics_consensus_2026-04-28.md` | File exists as referenced. |

### 4. Tests probe the right properties

- **goal1011** — asserts `wording.evidence == "Goal1058"` and `"oracle parity"` in
  `boundary` for both facility and robot; asserts `"timing-floor"` for robot. Exact
  match on `public_wording_blocked` status. ✓
- **goal1010** — asserts README contains `"after Goal1058"`, `"validated oracle
  parity"`, `"validated pose-flag oracle parity"`, and the consensus artifact
  trail link. ✓
- **goal1044** — asserts docs contain Goal1058, oracle parity, commit hash, and no
  stale "no readiness pod needed" wording. ✓
- **goal1025** — asserts `public_wording_blocked_apps == ["facility_knn_assignment",
  "robot_collision_screening"]` (exact list, exact order), and cloud_policy contains
  Goal1058. ✓
- **goal947** — asserts `reviewed_public_wording = 6`, `public_speedup_claim_authorized
  = False`, `public_wording_blocked` for both apps in checked-in JSON. ✓
- **goal1051** — asserts `diagnostic_reruns` contains both apps. ✓

All 25 tests passed as reported.

---

## Minor Issues (non-blocking)

**Dead test code in goal1044.** In
`test_status_page_records_goal1048_rerun_policy`, the filter
`public_wording_status != "public_wording_blocked"` excludes both facility and
robot from `ready_rows`, so the subsequent `if row["app"] in {facility,
robot}` branch can never execute. The test does not produce false passes
(the else-branch correctly covers non-blocked rows), and the substance it
intended to assert — that facility/robot cloud_action cites Goal1058 oracle
parity — is verified by goal1011, goal1044's other assertions, and the JSON
artifact. But the if-branch is unreachable dead code and should be cleaned up.

**Readiness `next_goal` not updated for facility.** `app_support_matrix.py`
line 506 still has `next_goal = "Goal887/Goal920"` (Goal1058 not added), while
`docs/v1_0_rtx_app_status.md` shows `Goal887/Goal920/Goal1058` in the Evidence
column. The discrepancy is cosmetic — the public wording matrix (which is what
Goal1059 targets) is correct, and no test relies on the readiness `next_goal`
field for this check.

---

## What Is Not Claimed and Confirmed Absent

- No public speedup ratio or numeric claim was introduced.
- No whole-app or broad RTX acceleration claim was introduced.
- No Goal1048 or Goal1058 evidence was promoted from diagnostic to claim-grade.
- The six previously Goal1009-reviewed sub-path rows are unchanged.
- `broad_or_whole_app_public_speedup_claim_authorized` remains `False` in all
  generated artifacts.
