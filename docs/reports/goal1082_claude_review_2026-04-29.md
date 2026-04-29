# Goal1082 Facility Same-Scale Baseline Intake — Claude Review

Date: 2026-04-29
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

---

## Scope

This review covers:

- `scripts/goal1082_facility_same_scale_baseline_intake.py`
- `tests/goal1082_facility_same_scale_baseline_intake_test.py`
- `docs/reports/goal1082_facility_same_scale_baseline_intake_2026-04-29.json`
- `docs/reports/goal1082_facility_same_scale_baseline_intake_2026-04-29.md`
- Source artifact: `docs/reports/goal1072_post_scale_up_rtx_pod_batch/facility_coverage_threshold_2_5m_timing.json`
- Source artifact: `docs/reports/goal1081_same_scale_baselines/facility_coverage_threshold_2_5m_cpu_oracle.json`

---

## Findings

### 1. Same-scale detection is correct

The script tests three independent conditions drawn directly from artifact fields:

| Condition | RTX artifact value | CPU oracle value | Match |
| --- | --- | --- | --- |
| `copies` | 2,500,000 | 2,500,000 | yes |
| query count / customer count | 10,000,000 | 10,000,000 | yes |
| `radius` | 1.0 | 1.0 | yes |

All three conditions are satisfied. `same_scale = True` is the correct computation from the stored artifacts.

### 2. The mismatch is real and sourced from saved artifacts

Both source artifacts are machine-generated records from prior goals and are not constructed or edited by this goal.

- RTX artifact (Goal1072 pod batch, Linux x86_64, OptiX mode, `skip_validation=true`): `threshold_reached_count = 8,898,102`, `all_queries_reached_threshold = false`, `matches_oracle = null`.
- CPU oracle (Goal1081, macOS arm64, dry-run mode, validation enabled): `covered_customer_count = 10,000,000`, `all_customers_covered = true`.

The script reads these values without transformation. `decision_matches = False` (False ≠ True) and `covered_count_matches = False` (8,898,102 ≠ 10,000,000) are the correct boolean results. The delta is 1,101,898 uncovered queries — approximately 11.0% — a substantial and unambiguous divergence, not a rounding artifact.

Note: `matches_oracle_in_artifact = null` because the RTX run was executed with `skip_validation = true`. No in-run oracle comparison was performed. The intake correctly surfaces this as an additional data point rather than suppressing it.

### 3. The BLOCK verdict is appropriate

`public_claim_authorized` requires all three checks — `same_scale`, `decision_matches`, and `covered_count_matches` — to be True. Two checks fail. The BLOCK is therefore a direct, non-discretionary consequence of the check logic, not an editorial judgment. Given a coverage miss of roughly 11% at the same scale and radius as the CPU oracle, and given that the RTX run had validation disabled so no in-run correctness check was performed, BLOCK is the only defensible outcome.

### 4. The precision explanation is correctly framed as a likely engineering cause, not a proven fact

The reason field reads: *"The likely engineering cause is coordinate precision at 2.5M copies: x coordinates reach about 15 million while the radius is 1.0, which is unsafe for float-oriented RT traversal without tiling, recentering, or another precision-aware mapping."*

The phrase "likely engineering cause" is used consistently throughout the script, the JSON output, and the markdown. The explanation is presented as a plausible hypothesis grounded in RT precision characteristics, not as a confirmed diagnosis. No other language in the script asserts this cause as proven. The framing is appropriate.

### 5. No public RTX speedup claim is authorized or implied

The intake enforces this boundary in three places that are independently checkable:

1. The `boundary` field in the output JSON and markdown explicitly states the goal "does not authorize public RTX speedup claims."
2. The first next action explicitly reads: "Do not publish a facility RTX speedup ratio from the current 2.5M timing row."
3. The test `test_markdown_keeps_honesty_boundary` asserts that the string "does not authorize public RTX speedup claims" is present in the rendered markdown.

The RTX query median (0.111 s) and CPU reference total (156.35 s) are recorded in the output for traceability but no ratio is computed, labeled, or presented as a speedup. The cloud claim contract in both source artifacts carries `activation_status: deferred_until_real_rtx_phase_run_and_review`, consistent with the intake outcome.

### 6. Minor observations (non-blocking)

- **`valid` field semantics**: `valid = same_scale and not public_claim_authorized` evaluates to True when the audit correctly detects a BLOCK condition. The field name could be read as "the RTX result is valid," but in context it means "this intake report is a valid (completed, non-contradictory) audit." The exit-code logic (`return 0 if payload["valid"] else 1`) is consistent with this reading: the script exits 0 when the audit ran to a definite conclusion, not when the RTX result passed. This is unconventional but internally consistent.
- **CPU oracle mode**: The oracle was generated in `dry-run` mode on arm64 macOS. Dry-run uses exact arithmetic and is the appropriate reference for a correctness oracle; it is not an RTX timing baseline. The intake does not conflate the two.
- **Test coverage**: Three test cases cover the BLOCK verdict, the exact mismatch counts, and the markdown honesty boundary. Coverage is proportionate to the scope.

---

## Summary

The same-scale detection is correct and verified against the saved artifact values. The mismatch — 8,898,102 RTX threshold-reaching queries versus 10,000,000 CPU-oracle-covered customers at identical scale parameters — is real, sourced from unmodified prior-goal artifacts, and unambiguous in magnitude. The BLOCK verdict follows directly from the check logic and is appropriate. The precision explanation is consistently qualified as a likely engineering cause. No public RTX speedup claim is made, authorized, or implied anywhere in the script, output, or tests.

**Verdict: ACCEPT**
