# Goal5515 LibRTS Range-Intersects Mismatch Resolution

Status: `implemented__historical_mismatches_no_longer_reproduced__review_pending`

## Objective

Recheck the two count disagreements recorded by Goal5500 after the generic
indexed-AABB validity correction, using the same official archive geometry and
query family. This is a resolution-of-observation goal, not a new performance
or paper-reproduction claim.

## Evidence

The current six-state gate is:

```text
Paper-reproduction-apps/librts-paper/results/goal5514_exact_range_intersects_select001_resolution_gate.json
```

The historical baseline is recorded in:

```text
history/internal_docs/goal5500_librts_exact_range_intersects_six_geometry_batch_result_2026-07-12.md
```

The official archive remains the MD5-verified `PPoPPAE-v2.tar.gz`; the same
geometry/query files are identified by SHA-256 in the Goal5513/5514 evidence.

## Result

| Case | Goal5500 RTDL delta | Current RTDL delta | Current state |
|---|---:|---:|---|
| `parks_Europe` | +3,791 | 0 | author/RTDL counts match |
| `lakes.bz2` | +54,695 | 0 | author/RTDL counts match |

The other three feasible cases in the family also match after the correction:
`dtl_cnty` 1,570,285, `USACensusBlockGroupBoundaries` 33,404,355, and
`USADetailedWaterBodies` 55,205,607. `parks.bz2` remains an explicit author
CUDA allocation failure, so RTDL was not run for that state.

This means the two historical disagreements no longer reproduce on the same
official query family after the generic correction. Goal5508 independently
established the relevant generic contract on float32-degenerate indexed AABBs;
this goal does not claim that every possible future discrepancy has one
universal cause.

## System significance

The change remains a generic RTDL AABB semantic correction. It does not add a
LibRTS primitive, paper-specific branch, or app-specific output behavior. The
LibRTS app only supplies official inputs, invokes the public columnar AABB
front door, and compares count results.

## Claim boundary

This closes only the observed `.01 x 10000` historical mismatch at the count
level. It does not close the 42-pair range-intersects inventory, prove
pairwise relation equality, reproduce Figure 6, authorize an author/RTDL
performance ratio, or claim full paper reproduction, zero-copy, author parity,
or Embree support.

The result is intentionally marked review pending.
