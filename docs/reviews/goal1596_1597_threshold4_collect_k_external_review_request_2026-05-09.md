# External Review Request: Threshold-4 OptiX Collect-K Gate

## Review Scope

Please review the threshold-4 experimental gate for OptiX `COLLECT_K_BOUNDED`.

The implementation is intentionally still opt-in:

```text
RTDL_OPTIX_COLLECT_K_GATED_CANDIDATE=1
```

The gate enables candidate carry-alias behavior only when static topology predicts at least four carry payload-copy reductions:

```text
baseline_carry_payload_copies >= candidate_carry_payload_copies + 4
```

Default behavior must remain unchanged. Public speedup claims and primitive promotion are explicitly out of scope.

## Files To Review

- `src/native/optix/rtdl_optix_api.cpp`
- `scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py`
- `tests/goal1593_v1_5_4_optix_collect_k_gated_candidate_test.py`
- `docs/reports/goal1596_v1_5_4_optix_collect_k_threshold4_gate_rtx4090_validation_2026-05-09.md`
- `docs/reports/goal1597_v1_5_4_optix_collect_k_threshold4_gate_rtx3090_validation_2026-05-09.md`

## Evidence Summary

RTX 4090, commit `9042a86ace691a5dedfdf37e29c5ffbb7f588baa`:

| Candidate count | Avg delta ms | Faster rounds | Payload-copy change |
|---:|---:|---:|---|
| 65536 | 0.000796 | 4/5 | 0 -> 0 |
| 65537 | -0.009974 | 5/5 | 5 -> 0 |
| 65538 | -0.009972 | 5/5 | 5 -> 0 |
| 65552 | -0.011182 | 5/5 | 5 -> 0 |
| 69632 | -0.008774 | 5/5 | 4 -> 0 |
| 69633 | 0.000721 | 3/5 | 4 -> 4 |

RTX 3090, commit `8589cf4ecdc617bc628a3ce0d9073eac277c24ea`:

| Candidate count | Avg delta ms | Faster rounds | Payload-copy change |
|---:|---:|---:|---|
| 65536 | -0.002928 | 3/5 | 0 -> 0 |
| 65537 | -0.016960 | 5/5 | 5 -> 0 |
| 65538 | -0.017864 | 5/5 | 5 -> 0 |
| 65552 | -0.014888 | 5/5 | 5 -> 0 |
| 69632 | -0.017704 | 5/5 | 4 -> 0 |
| 69633 | 0.000514 | 3/5 | 4 -> 4 |

All measured artifacts reported accepted Goal1506 evidence, parity pass, and expected topology.

## Review Questions

1. Does the threshold-4 gate look technically justified as an internal experimental opt-in policy?
2. Are there implementation or testing risks that should block keeping this opt-in mode in `main`?
3. Is the claim boundary sufficiently conservative?
4. Should we stop GPU pod cycling for this micro-goal and move to broader architecture/release work?

## Required Verdict Format

Please answer with:

- `Verdict`: acceptable / acceptable-with-changes / not acceptable
- `Findings`: concrete issues, if any
- `Recommendation`: whether to stop more pod work for this micro-goal
- `Claim Boundary`: whether the no-promotion/no-public-speedup boundary is clear
