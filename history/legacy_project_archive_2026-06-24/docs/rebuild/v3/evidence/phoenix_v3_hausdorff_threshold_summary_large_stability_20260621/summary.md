# Phoenix V3 Hausdorff Threshold-Summary Large-Row Stability Evidence

status: hausdorff_threshold_summary_large_stability_evidence_not_promoted

This artifact repeats the largest Hausdorff threshold-summary candidate
as independent process runs. It repairs the external-review request for
stability data; it does not authorize promotion by itself.

## Scope

- Copies: `262144`
- Points per side: `1048576`
- Threshold: `0.4`
- Independent paired samples: `5`
- Inner repeat/warmup per sample: `5` / `1`

## Summary

- All pairs match oracle: `True`
- All pairs same decision: `True`
- All phase-total pairs above 1x: `True`
- Weakest phase-total OptiX/Embree speedup: `1.2243669013234328`
- Phase-total ratio mean/stddev: `1.240042444838897` / `0.01179874030631055`
- Query ratio mean/stddev: `1.6386841066991966` / `0.020920743964462737`
- Wrapper ratio mean/stddev: `1.5558395967131606` / `0.015463555481955769`

## Paired Samples

| Sample | Embree query | OptiX query | Query speedup | Embree phase total | OptiX phase total | Phase speedup | Wrapper speedup | Oracle |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 9.81722 | 6.01283 | 1.63271x | 19.1627 | 15.6511 | 1.22437x | 1.54865x | `True` |
| 2 | 10.2564 | 6.11994 | 1.6759x | 19.8792 | 15.8515 | 1.25409x | 1.58328x | `True` |
| 3 | 9.97427 | 6.13073 | 1.62693x | 19.6563 | 15.8056 | 1.24363x | 1.54797x | `True` |
| 4 | 10.1424 | 6.2225 | 1.62995x | 19.7248 | 15.8292 | 1.2461x | 1.55222x | `True` |
| 5 | 9.93514 | 6.10295 | 1.62793x | 19.471 | 15.8041 | 1.23202x | 1.54708x | `True` |

## Oracle Definition

The oracle is expected_tiled_hausdorff(copies=N): the app computes the exact Hausdorff summary on the four-point authored base fixture using brute force, then scales deterministic row-count metadata by N because the benchmark input is a tiled repetition of that fixture. The threshold-summary route checks both directed fixed-radius decisions against oracle_within_threshold = oracle['hausdorff_distance'] <= threshold.

## Claim Boundary

- Not full exact Hausdorff distance or witness materialization.
- Not X-HD paper reproduction.
- Not broad V3-over-V2 wording.
- Not all threshold values.
- Not all sizes.
- Not M7 until the evidence packet, external review, and Codex consensus are updated.

