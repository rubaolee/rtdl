# Goal1096 Claude Review — Current RTX Pod Artifact Intake

Date: 2026-04-29  
Reviewer: Claude (claude-sonnet-4-6)  
Scope: `scripts/goal1096_current_rtx_pod_artifact_intake.py`, `tests/goal1096_current_rtx_pod_artifact_intake_test.py`, `docs/reports/goal1096_current_rtx_pod_artifact_intake_2026-04-29.{json,md}`, and source packets `goal1084_facility_recentered_rtx_pod_packet.py`, `goal1093_barnes_hut_20m_contract_packet.py`.

Overall verdict: **PASS WITH TWO FINDINGS**

The intake correctly implements all five required behaviors. Two issues are noted: one design-level concern and one test-coverage gap. Neither blocks the intake's current use.

---

## 1. Missing-artifact handling

**Verdict: PASS**

`_review_row` checks `path.exists()` before attempting to load JSON. When a file is absent it immediately returns `artifact_status="missing"` and `review_status="needs_cloud_artifact"` with a clear reason string. `build_intake` aggregates these into `missing_artifact_count` and sets `overall_status="needs_cloud_artifacts"` when any are absent and nothing is blocked. The intake never silently skips a missing artifact or treats absence as a pass.

The current runtime state (`goal1096_current_rtx_pod_artifact_intake_2026-04-29.json`) confirms all three expected artifacts are missing and the status is correctly `needs_cloud_artifacts`.

**Note (Finding 1 — see Section 7):** `valid=True` is set even when `missing_artifact_count=3`. This is intentional and tested, but the semantics are worth flagging.

---

## 2. Bad-validation blocking

**Verdict: PASS**

`_validate_facility` requires `_nested(artifact, ("scenario", "result", "matches_oracle")) is True` (strict identity, not truthiness). Any value other than the boolean `True` — including `None`, `False`, or a missing key — returns `("blocked", ...)`. The same check is applied in `_validate_barnes` on the validation row (`requires_validation=True`). `build_intake` converts any `blocked` row into a non-zero `blocked_count`, which forces `overall_status="blocked"` regardless of the other rows' status.

`test_facility_bad_oracle_blocks` exercises this path end-to-end, verifying that a facility artifact with `matches_oracle=False` yields `overall_status="blocked"`, `blocked_count=1`, and `valid=False`.

---

## 3. Skip-validation policy enforcement

**Verdict: PASS**

`_validate_common` cross-checks the artifact's `parameters.skip_validation` flag against the packet row's `contains_skip_validation` field:

```python
if bool(_nested(artifact, ("parameters", "skip_validation"))) != bool(row["contains_skip_validation"]):
    return False, "artifact skip_validation does not match packet row"
```

The packet rows declare the correct policy:
- Facility validation row: `contains_skip_validation=False`
- Barnes-Hut validation row (`depth8_contract_validation`): `contains_skip_validation=False`
- Barnes-Hut timing row (`depth8_20m_timing_repeat`): `contains_skip_validation=True`

An artifact arriving with `skip_validation=True` on either validation row will be blocked before `matches_oracle` is inspected. An artifact arriving with `skip_validation=False` on the timing row will likewise be blocked. The boolean cast on both sides prevents `None`/missing from silently matching `False`.

**Note (Finding 2 — see Section 8):** The test suite does not exercise a skip-validation mismatch directly; this path is covered by code inspection but not by a dedicated test case.

---

## 4. Timing floor checks

**Verdict: PASS**

Both `_validate_facility` and `_validate_barnes` (timing row) check:

```python
if isinstance(floor, (int, float)) and phase_sec < float(floor):
    return "timing_below_floor", f"... {phase_sec:.6f}s is below {float(floor):.3f}s floor", phase_sec
```

The `isinstance` guard correctly handles `timing_floor_sec=None` on the Barnes-Hut validation row — when the floor is absent, no timing check is performed. For rows that do declare a floor (facility: 0.100 s, Barnes-Hut timing: 0.100 s), any artifact reporting a median below that floor is returned with `review_status="timing_below_floor"`, which maps to `overall_status="timing_floor_not_met"` in `build_intake`.

`test_barnes_timing_floor_not_met_is_not_claim_ready` exercises this: all three artifacts present, the timing row reports `median_sec=0.01` (below the 0.100 s floor), and the result is `overall_status="timing_floor_not_met"` with `valid=True` (no blocking error, but not claim-ready either).

---

## 5. Public RTX claim authorization

**Verdict: PASS — claims are unconditionally suppressed**

`public_speedup_claim_authorized` is hardcoded `False` in every row dict produced by `_review_row` (line 119 of the intake script). There is no code path that sets it to `True`. At the summary level, `public_speedup_claim_authorized_count` is hardcoded `0` (line 203). The `boundary` string — written to both JSON and Markdown output — explicitly states:

> "does not run cloud, does not change public wording, does not authorize release, and does not authorize public RTX speedup claims."

`test_cli_writes_intake_files` checks that the Markdown output contains "does not authorize public RTX speedup claims". `test_all_current_artifacts_pass_but_do_not_authorize_claims` confirms that even a fully-passing intake (all three artifacts present, oracle parity proven, timing floors met) sets `public_speedup_claim_authorized_count=0` and `overall_status="ready_for_2ai_review_not_public_claim"` — the status name itself encodes the prohibition.

The `overall_status` value `ready_for_2ai_review_not_public_claim` is the highest the intake can emit; there is no `claim_authorized` state.

---

## 6. Source-packet fidelity

**Verdict: PASS**

The intake imports both source packets' `build_packet()` functions at call time rather than reading cached JSON files. This means the intake always reflects the live packet definition — a packet-side change (e.g., updating a timing floor) takes effect immediately on the next intake run without any intermediate manual step.

The packet scripts correctly declare their own `valid` guards internally. Goal1084's `valid` check asserts: 1 row, `requires_validation=True`, `contains_skip_validation=False`, `timing_floor_sec=0.100`, scenario `facility_service_coverage_recentered`, and `--copies 2500000`. Goal1093's `valid` check asserts: 2 rows with matching depth-8 / node-count-65536 / threshold-4 / radius-0.1 parameters, row[0] is validation-only, row[1] carries `skip_validation` and `timing_floor_sec=0.100`.

---

## 7. Finding 1 — `valid=True` with all artifacts missing (design concern, not a defect)

`build_intake` sets `"valid": blocked_count == 0`. Because missing artifacts produce `review_status="needs_cloud_artifact"` rather than `"blocked"`, the `valid` flag is `True` even when `missing_artifact_count=3`.

This is intentional and tested (`test_missing_artifacts_require_cloud` asserts `payload["valid"] is True` with 3 missing artifacts). The rationale appears to be: `valid=False` means "a validation failure was found," while `overall_status="needs_cloud_artifacts"` means "the evidence chain is incomplete." These are two orthogonal signals, and any consumer must read `overall_status` to determine readiness.

The risk is that a downstream consumer reading only `valid=True` could incorrectly conclude the intake passed. This review recommends that any consumer of this intake be required to check `overall_status` explicitly and that documentation note the distinction. No code change is required at this time.

---

## 8. Finding 2 — Test-coverage gap for several blocking paths

The test suite covers five scenarios: missing artifacts, happy path, bad oracle on facility, timing floor not met, and CLI output. The following blocking paths are confirmed by code inspection but have no dedicated test:

| Uncovered path | Expected behavior |
| --- | --- |
| Artifact `skip_validation` does not match packet row | `review_status="blocked"` |
| Artifact `schema_version` is wrong | `review_status="blocked"` |
| Artifact `scenario.mode` is not `"optix"` | `review_status="blocked"` |
| Facility artifact missing `coordinate_mapping` | `review_status="blocked"` |
| Barnes-Hut wrong `barnes_tree_depth`, `node_count`, or `hit_threshold` | `review_status="blocked"` |
| Barnes-Hut timing row with no `optix_query_sec` median | `review_status="blocked"` |
| Unreadable / malformed JSON | `review_status="blocked"` |
| Unknown `app` field | `review_status="blocked"` |

These gaps do not affect the current intake run (all artifacts are missing), but they should be closed before the intake is used to adjudicate real cloud artifacts.

---

## 9. Current runtime state

As of 2026-04-29 the intake reports:

| Field | Value |
| --- | --- |
| `overall_status` | `needs_cloud_artifacts` |
| `expected_artifact_count` | 3 |
| `present_artifact_count` | 0 |
| `missing_artifact_count` | 3 |
| `blocked_count` | 0 |
| `timing_below_floor_count` | 0 |
| `public_speedup_claim_authorized_count` | 0 |
| `valid` | `true` |

The cloud RTX pod run has not yet been copied back. No evidence has been reviewed. No public claims are authorized. The intake is waiting for:

1. `docs/reports/goal1084_facility_recentered_rtx_pod_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json`
2. `docs/reports/goal1093_barnes_hut_20m_contract/barnes_hut_depth8_4096_validation.json`
3. `docs/reports/goal1093_barnes_hut_20m_contract/barnes_hut_depth8_20m_timing.json`

---

## 10. Summary

| Check | Result |
| --- | --- |
| Waits for missing artifacts (does not pass early) | PASS |
| Blocks on bad oracle parity | PASS |
| Enforces skip-validation policy | PASS |
| Enforces timing floors | PASS |
| Never authorizes public RTX speedup claims | PASS |
| Source-packet fidelity | PASS |
| `valid` semantics with missing artifacts | Finding 1 (design concern, intentional, no code change required) |
| Test coverage of all blocking paths | Finding 2 (gap, recommend closing before adjudicating real artifacts) |

The intake is suitable for its current purpose: waiting for cloud artifacts and providing a clear readiness gate before 2AI review. No blocking issues are identified.
