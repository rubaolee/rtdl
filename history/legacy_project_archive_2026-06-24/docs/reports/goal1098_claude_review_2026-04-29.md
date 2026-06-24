# Goal1098 Claude Review — RTX A5000 Goal1084/Goal1093 Evidence

Date: 2026-04-29  
Reviewer: Claude (claude-sonnet-4-6)  
Branch: codex/rtx-cloud-run-2026-04-22  
Source commit under review: `58ca06f2573d53754663a2dd10a76207113ab044`

---

## Evidence Reviewed

| File | Role |
| --- | --- |
| `goal1098_rtx_a5000_goal1084_goal1093_execution_report_2026-04-29.md` | Primary execution record |
| `goal1096_current_rtx_pod_artifact_intake_2026-04-29.json` | Intake gate output |
| `goal1084_facility_recentered_rtx_pod_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json` | Goal1084 artifact |
| `goal1093_barnes_hut_20m_contract/barnes_hut_depth8_4096_validation.json` | Goal1093 validation artifact |
| `goal1093_barnes_hut_20m_contract/barnes_hut_depth8_20m_timing.json` | Goal1093 20M timing artifact |
| `cloud_session_2026_04_29/goal1084_runner.log` | Pod execution log (Goal1084) |
| `cloud_session_2026_04_29/goal1093_runner.log` | Pod execution log (Goal1093) |
| `scripts/goal887_prepared_decision_phase_profiler.py` | Profiler source (post-patch) |
| `tests/goal887_prepared_decision_phase_profiler_test.py` | Profiler tests |

---

## Finding 1 — Goal1096 Status `ready_for_2ai_review_not_public_claim`

**Verdict: SUPPORTED**

The intake JSON reports:

- `overall_status: "ready_for_2ai_review_not_public_claim"`
- `valid: true`
- `present_artifact_count: 3`, `missing_artifact_count: 0`
- `blocked_count: 0`
- `public_speedup_claim_authorized_count: 0`

All three rows carry consistent artifact statuses:

| Artifact | review_status | rtx_phase_sec (median) | timing_floor_sec |
| --- | --- | ---: | ---: |
| facility recentered 2.5M | `validation_and_timing_passed` | 0.13505 | 0.1 |
| Barnes-Hut depth-8 4096 | `validation_passed` | 0.007582 | — |
| Barnes-Hut depth-8 20M | `timing_floor_passed` | 0.23064 | 0.1 |

Both timing-floor artifacts exceed the 100 ms floor. The validation-only Barnes-Hut row (4096 bodies) carries `matches_oracle: true` with 65,536 nodes at depth 8 and all 4,096 queries reaching threshold — parity is established. The 20M timing repeat correctly carries `matches_oracle: null` because it ran with `--skip-validation`; this is consistent with the contract (parity delegated to the 4096 validation run).

Both runner logs independently confirm the same GPU (NVIDIA RTX A5000, 24,564 MiB, driver 565.57.01) and match the environment table in the execution report. The runner log timestamps are consistent with the `generated_at` fields in the artifacts (all 2026-04-29 between 11:08 and 11:14 UTC).

---

## Finding 2 — Source-Commit Stamping Disclosure

**Verdict: ADEQUATELY DISCLOSED; FUTURE-RUN FIX CONFIRMED**

**What happened on the pod**: The profiler did not embed `source_commit` natively during the cloud run. The execution report explains that the source commit was subsequently stamped from `.rtdl_source_commit` by Codex, which added a `source_commit_note` field to each artifact without altering any timing or result fields.

**Disclosure quality**: Every artifact carries both fields:

```json
"source_commit": "58ca06f2573d53754663a2dd10a76207113ab044",
"source_commit_note": "Stamped from .rtdl_source_commit after run because Goal887 profiler
  does not embed RTDL_SOURCE_COMMIT. Runner log also records the same commit.
  Timing/result fields are unchanged."
```

Both runner logs record `source_commit=58ca06f2573d53754663a2dd10a76207113ab044` as their first data line, providing an independent, pre-copy-back confirmation of the same commit. The disclosure is transparent and internally consistent.

**Post-patch state**: The current profiler source (`scripts/goal887_prepared_decision_phase_profiler.py:100-118`) implements `_source_commit()`, which reads `RTDL_SOURCE_COMMIT` env var, then `.rtdl_source_commit`, then falls back to `git rev-parse HEAD`. The `run_profile()` function at line 493 now embeds `source_commit` natively. The test at line 58 of the test file verifies `payload["source_commit"] == "goal887-test-commit"` when `RTDL_SOURCE_COMMIT` is set. The patch is real and in place.

**Residual note**: Post-hoc stamping is not ideal because it creates a window in which the artifact files lacked a source commit. That window is closed by disclosure and by independent runner log evidence. For future pod runs the issue is structurally resolved by the patch.

---

## Finding 3 — No Public Speedup or Release Claim Authorized

**Verdict: CONFIRMED — ZERO CLAIMS AUTHORIZED**

Every layer of the evidence chain carries explicit prohibitions:

1. **Intake gate** (`goal1096_...intake.json`): `public_speedup_claim_authorized_count: 0`; every row has `public_speedup_claim_authorized: false`.

2. **Each artifact**: `cloud_claim_contract.activation_status: "deferred_until_real_rtx_phase_run_and_review"` and a `boundary` field reading: *"It does not authorize an RTX speedup claim without a real RTX run, same-semantics baselines, and independent review."*

3. **Execution report boundary section**: *"This report does not claim whole-app speedup, does not compare against baselines, does not authorize public README/front-page wording, and does not authorize a release."*

4. **No CPU baselines are present** in any artifact, which structurally prevents a speedup ratio from being computed. The claim contract's `required_phase_groups` list covers only the OptiX phases; CPU reference phases are absent from all three artifacts, consistent with timing-only data collection in the correct gate.

---

## Summary

| Question | Verdict |
| --- | --- |
| Does evidence support Goal1096 status `ready_for_2ai_review_not_public_claim`? | **Yes** |
| Is source-commit stamping adequately disclosed? | **Yes** (post-hoc stamp transparent; runner logs corroborate; patch in place) |
| Is any public speedup or release claim authorized? | **No** (zero authorized across all artifacts and intake) |

The artifact set is internally consistent, the GPU hardware is confirmed by runner logs, parity is established for the validation runs, timing floors are met, and all claim boundaries are intact. This evidence is ready for the next required 2+ AI review step. No further action is blocked pending that review.
