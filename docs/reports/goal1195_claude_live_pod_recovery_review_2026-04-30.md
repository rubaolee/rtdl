# Goal1195 Claude Live Pod Recovery Review

Verdict: `ACCEPT`

The Goal1194 live-pod recovery trail is acceptable as evidence-readiness for
public-wording review.

## Findings

1. Final bundle:
   All 12 artifacts pass schema, parity, and timing floor. All 6 pairs are
   intake-ready. One non-blocking discrepancy: the final intake's archive check
   found no tgz because it searched the wrong relative path. The bundle and
   SHA256 are cited in the recovery report, so this does not block
   evidence-readiness.

2. Bootstrap fixes:
   `cuda-nvcc-13-0` and `libembree-dev` are missing-package installs only. They
   restore the expected compile-time environment without touching app logic,
   benchmark contracts, or schemas. The prior Goal1194 packet is not
   invalidated.

3. Jaccard instability:
   The first-run parity failure is documented and the chunk-sensitivity
   explanation is plausible. The final chunk-512 artifact passes schema and
   parity, so it is acceptable for evidence-readiness. However, Jaccard's final
   raw ratio is `0.549`, meaning OptiX is slower than Embree. Any public wording
   listing Jaccard must note the first-run failure and that the result shows
   OptiX slower than Embree.

4. Scope boundary:
   Evidence supports evidence-readiness only. Four of six apps show OptiX slower
   than Embree on the measured phase. Only `road_hazard_screening` and
   `hausdorff_distance` show OptiX advantage, and those must be scoped to the
   specific measured sub-path.

## Required Fixes

None blocking.

## Capture Note

This review was produced by `claude --print --dangerously-skip-permissions` and
saved by Codex because Claude returned the verdict in stdout.
