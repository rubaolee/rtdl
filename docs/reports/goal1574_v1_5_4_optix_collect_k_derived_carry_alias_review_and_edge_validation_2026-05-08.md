# Goal 1574: Derived Carry Alias Review And Edge Validation

## Verdict

Keep `RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC=1` as a positive diagnostic candidate, not a production default yet.

Goal1574 added one external Claude review and a small edge/topology validation pass. The result strengthens Goal1573: the topology guard still preserves accepted parity, and additional odd long cases improve without adding host/device descriptor traffic. However, promotion should wait for broader topology coverage and at least one additional GPU architecture.

## Claude Review

Saved review:

- `docs/reviews/goal1573_derived_carry_alias_claude_review_2026-05-08.md`

Claude's recommendation was:

- The guard is logically sound.
- The feature should remain diagnostic until broader tests pass.
- The current `carry_copies`/internal-transfer accounting is topology-oriented and should be clarified before promotion.
- Additional GPU architectures and wider even/odd sweeps are recommended before public speedup wording.

## Edge Validation

Pod:

- `root@157.157.221.29 -p 22942`
- NVIDIA RTX 4000 Ada Generation, driver `550.127.05`
- Commit: `f4e13c59502546b4fe968fba9a69371755539194`

Diagnostic edge run:

- Env: baseline Goal1506 OptiX collect-k flags plus `RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC=1`
- Counts: `3`, `5`, `7`, `32769`, `49153`
- Result: accepted Goal1506 evidence, parity passed, native paths matched, profile topologies matched.

The tiny `3`, `5`, and `7` cases route through `row_width2_parallel_bitonic_sort`; the derived carry alias is inactive there and parity remains clean.

## Measured Comparison

| Case | Baseline stage total ms | Alias stage total ms | Baseline carry ms | Alias carry ms | Parity |
|---:|---:|---:|---:|---:|---|
| 32769 | 0.216400 | 0.203125 | 0.028343 | 0.014959 | Pass |
| 49153 | 0.219806 | 0.212853 | 0.021370 | 0.015239 | Pass |

This is consistent with Goal1573: the optimization helps odd-carry long cases while leaving non-carry or non-merge paths neutral.

## Accounting Note

The existing profile field `carry_copies` behaves as a topology counter: it increments when a carry segment exists. It should not currently be interpreted as "payload row copies executed" after the derived carry alias diagnostic, because the diagnostic can alias the row payload while still copying the carry count device-to-device.

Before production promotion, the profiler should either:

- keep `carry_copies` as topology and add a separate payload-copy counter, or
- rename/clarify the field so reports do not overstate device row-copy work.

## Next Gate

Do not promote to default yet. The next gate should include:

- a bounded even/odd sweep that avoids the oversized long run that timed out,
- explicit blocked-alias topology cases where the guard must fall back to copying,
- one more NVIDIA architecture if available,
- a profiler accounting clarification.

No public speedup claim, stable primitive promotion, or release action is authorized by this report.

## Artifacts

- `docs/reports/goal1574_v1_5_4_optix_collect_k_derived_carry_alias_edge_profile_2026-05-08.json`
- `docs/reports/goal1574_v1_5_4_optix_collect_k_derived_carry_alias_edge_profile_2026-05-08.md`
- `docs/reports/goal1574_v1_5_4_optix_collect_k_derived_carry_alias_edge_baseline_profile_2026-05-08.json`
- `docs/reports/goal1574_v1_5_4_optix_collect_k_derived_carry_alias_edge_baseline_profile_2026-05-08.md`
