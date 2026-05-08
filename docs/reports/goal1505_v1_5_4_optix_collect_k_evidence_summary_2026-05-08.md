# Goal 1505: OptiX COLLECT_K_BOUNDED Evidence Summary

## Verdict

`goal1505_optix_collect_k_evidence_summary_recorded`

This is an evidence registry, not a new measurement and not a release action.

## Source Artifacts

- `docs/reports/goal1502_v1_5_4_python_optix_collect_k_bounds_probe_2026-05-08.json`: goal=`Goal1502`, status=`goal1502_python_optix_collect_k_bounds_and_dynamic_width_probe_passed`, device=`NVIDIA RTX 4000 Ada Generation`, commit=`b42ac66332355fc6f3b3e5e957f65a9d8597c54a`
- `docs/reports/goal1502_v1_5_4_python_optix_collect_k_bounds_probe_blackwell_2026-05-08.json`: goal=`Goal1502`, status=`goal1502_python_optix_collect_k_bounds_and_dynamic_width_probe_passed`, device=`NVIDIA RTX PRO 4500 Blackwell`, commit=`fd33cad297acaadcb90efd79e240308a81798918`
- `docs/reports/goal1503_v1_5_4_optix_collect_k_scaling_probe_2026-05-08.json`: goal=`Goal1503`, status=`goal1503_optix_collect_k_scaling_probe_recorded`, device=`NVIDIA RTX 4000 Ada Generation`, commit=`0ef25617af5ee656f9d7933794fc13a750095b9c`
- `docs/reports/goal1503_v1_5_4_optix_collect_k_scaling_probe_blackwell_2026-05-08.json`: goal=`Goal1503`, status=`goal1503_optix_collect_k_scaling_probe_recorded`, device=`NVIDIA RTX PRO 4500 Blackwell`, commit=`fd33cad297acaadcb90efd79e240308a81798918`
- `docs/reports/goal1504_v1_5_4_optix_collect_k_tiled_overflow_probe_2026-05-08.json`: goal=`Goal1504`, status=`goal1504_optix_collect_k_tiled_overflow_probe_recorded`, device=`NVIDIA RTX PRO 4500 Blackwell`, commit=`fd33cad297acaadcb90efd79e240308a81798918`

## Evidence Scope

- Primitive: `experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge`
- Row_width=2 fast/tiled path max candidate count: `131072`
- Dynamic row-width validated: `True`
- INT64_MAX pair validated: `True`
- Overflow fail-closed validated: `True`
- Measured devices: `NVIDIA RTX 4000 Ada Generation, NVIDIA RTX PRO 4500 Blackwell`

## Scaling

- `ada`: device=`NVIDIA RTX 4000 Ada Generation`, cases=`19`, max_candidates=`131072`, max_candidate_median_ms=`189.755149`, tiled_cases=`10`, all_parity_passed=`True`
- `blackwell`: device=`NVIDIA RTX PRO 4500 Blackwell`, cases=`3`, max_candidates=`131072`, max_candidate_median_ms=`181.992388`, tiled_cases=`3`, all_parity_passed=`True`

## Overflow

- Device: `NVIDIA RTX PRO 4500 Blackwell`
- Candidate counts: `[4097, 65537, 131072]`
- All fail-closed passed: `True`

## Claim Boundary

Goal1505 only indexes already committed Goal1502/Goal1503/Goal1504 OptiX COLLECT_K_BOUNDED artifacts. It records that real NVIDIA parity, bounded row_width=2 scaling through 131072 candidates, dynamic-width behavior, INT64_MAX row behavior, and fail-closed overflow behavior have evidence. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, experimental public promotion, release action, or any new GPU claim.
