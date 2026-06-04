# Goal3230: RayJoin Public Count Claim-Boundary Normalization

Date: 2026-06-03

## Purpose

Goal3230 closes the informational claim-boundary inconsistency carried forward
from the Goal3226 and Goal3228 Claude reviews.

Before this cleanup, the Goal3225 and Goal3227 public RayJoin count artifacts
used the canonical six false claim flags at the top and row levels, while the
nested per-measurement blocks inherited an older workload-level key set. All
values were already `false`, so this was not a claim leak, but it made the
artifacts harder to machine-check.

## Change

The public overlay and PIP probe scripts now replace nested measurement-level
claim boundaries with the same canonical six false flags used by the row and
top-level blocks:

- `public_speedup_claim_authorized: false`
- `rt_core_speedup_claim_authorized: false`
- `true_zero_copy_claim_authorized: false`
- `rayjoin_paper_reproduction_claim_authorized: false`
- `rtdl_beats_rayjoin_claim_authorized: false`
- `release_authorized: false`

The refreshed pod artifacts were produced at commit
`92e16b8649f99aa62fbca0d0c97466a7a2f8eaa3`.
The canonical boundary is now present at the top, row, and measurement levels.

## Refreshed Evidence

| Artifact | Cases | Counts | Median Prepared/Count Time |
| --- | --- | --- | --- |
| Goal3225 overlay | `overlay_county128_soil128`, `overlay_county256_soil256` | `1/1`, `9/9` | 0.022716183215379715 s, 0.05908652022480965 s |
| Goal3227 PIP | `pip_county512` | `1430/1430` | 0.06793256662786007 s |

The counts remain unchanged from the previous evidence: overlay active seeds
match the CPU `active_seed_count` contract, and PIP matches the CPU
`positive_assignment_count` contract.

## Validation

- `tests.goal3225_rayjoin_public_overlay_active_count_probe_test`
- `tests.goal3227_rayjoin_public_pip_count_probe_test`
- `tests.goal3225_rayjoin_public_overlay_active_count_probe_artifact_test`
- `tests.goal3227_rayjoin_public_pip_count_probe_artifact_test`
- `tests.goal3229_rayjoin_public_count_coverage_summary_test`
- `tests.goal3230_rayjoin_public_count_claim_boundary_normalization_test`

## Boundary

This cleanup does not authorize release, public speedup claims, broad RT-core
claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims. In short: no RayJoin paper-reproduction claims are
authorized here. It only makes the existing public count/parity evidence easier
to audit.
