# Goal3550: Goal3536 Observed-Target Summary Fields

Status: accepted local harness hardening.

Goal3548 exposed a usability gap in the Goal3536 steady-state packet: the generated summary reported `target_met_by_plan_pair_count`, but not the count of rows that actually met the observed measured-time target after execution. A reviewer had to inspect `rows[*].execution.target_met_by_observed_sum` manually to find the RTNN v2.3 undershoot.

## Change

`scripts/goal3536_v2_8_vs_v2_3_10s_steady_state.py` now adds these fields:

- `comparisons[*].v23_observed_measured_sec`
- `comparisons[*].v28_observed_measured_sec`
- `summary.target_met_by_observed_pair_count`
- `summary.observed_target_miss_count`
- `summary.observed_target_misses`

The rendered Markdown table now has separate columns for:

- `Target plan met?`
- `Target observed met?`

## Why This Matters

The repeat planner can be correct and still undershoot if a row becomes faster than its seed during the next calibrated pass. Goal3548 showed exactly that for RTNN v2.3. Future packets should surface that gap at the summary level without a manual JSON audit.

## Boundary

This is a measurement-harness clarity change only. It does not change benchmark commands, app implementations, native code, partner code, or claim authorization.

## Validation

Command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3536_v2_8_vs_v2_3_10s_steady_state_test tests.goal3548_v2_9_a5000_same_contract_repeat_evidence_test
```

Result: `10 tests OK`.

