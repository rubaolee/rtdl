# Codex Consensus: Goal 201 Fixed-Radius Neighbors External Baselines

## Verdict

Goal 201 is the right next `v0.4` slice and is implemented in a bounded,
honest way.

## Findings

- SciPy is used as the primary external CPU baseline without becoming part of
  the RTDL truth path.
- PostGIS is present only as a bounded comparison helper.
- Both external paths re-apply RTDL contract semantics instead of inheriting
  backend-native row order.
- Optional dependencies remain optional; the normal first-run path is still the
  RTDL truth/runtime path.

## Summary

This goal gives `fixed_radius_neighbors` its first external comparison story
without turning `v0.4` into a database-wrapper milestone. The scope stays
aligned with the settled plan: correctness and comparison first, performance
claims later.
