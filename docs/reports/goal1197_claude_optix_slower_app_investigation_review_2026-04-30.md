# Goal1197 Claude OptiX Slower-App Investigation Review

Verdict: `ACCEPT`

## Findings

1. The manifest correctly targets exactly the four app paths where the accepted
   Goal1195 evidence showed OptiX slower than Embree:
   `database_analytics`, `graph_analytics`,
   `polygon_pair_overlap_area_rows`, and `polygon_set_jaccard`.

2. The hypotheses and scale sweeps are sufficient to distinguish fixed GPU
   launch/setup/interface overhead from proportional traversal cost. Database
   uses a 10x range, graph uses a 4x range, and Jaccard holds copies fixed while
   sweeping chunk size for stability.

3. The Jaccard stability rule is strict enough: any chunk configuration that
   fails parity blocks the app entirely. This is appropriate after the observed
   chunk-sensitive or nondeterministic behavior.

4. `road_hazard_screening` and `hausdorff_distance` are correctly included only
   as positive controls. If either positive control fails to reproduce its
   accepted advantage, the slower-app measurements should not be trusted.

5. The manifest preserves the no-public-wording and no-release boundary.

## Advisory

The original polygon-pair sweep changed `chunk_copies` from `100` to `200` at
the largest copy scale, which could conflate copy-count scaling with chunk-size
effects. This was non-blocking but should be fixed before pod execution.

## Required Fixes

None blocking.

## Capture Note

This review was produced by `claude --print --dangerously-skip-permissions` and
saved by Codex because Claude returned the verdict in stdout.
