# Goal2533 Barnes-Hut Generic Force Contributions

Date: 2026-05-23

## Decision

Barnes-Hut force accumulation is now expressed through app-agnostic RTDL
reference contracts before the app-specific final interpretation step:

- `generic_weighted_inverse_square_contribution_rows_2d_v1`
- `generic_grouped_vector_sum_rows_2d_v1`

This continues Goal2532. Goal2532 made the tree and opening frontier generic;
Goal2533 makes the vector contribution and vector-sum reduction generic.

## What Changed

Implemented in `src/rtdsl/aggregate_tree_reference.py`:

- `evaluate_weighted_inverse_square_contribution_rows_2d(...)`
- `sum_vector_contribution_rows_2d(...)`
- contract exports through `src/rtdsl/__init__.py`

Updated the Barnes-Hut benchmark wrapper:

- added `force_contributions_bucketized_cpu`
- changed `bucketized_force_cpu` to use the generic contribution rows and
  grouped vector-sum rows instead of directly calling app-local force helpers

The app still owns body generation, theta/bucket policy, and final reporting.
The force law and grouped vector sum are now generic reference surfaces.

## Local Evidence

Timing artifact:

- `docs/reports/goal2533_barnes_hut_generic_force_contributions_local_2026-05-23.json`

At 2,048 bodies with bucket size 32:

- contribution rows: 258,495
- aggregate contribution rows: 54,264
- exact contribution rows: 204,231
- `force_contributions_bucketized_cpu`: 493.35 ms
- `bucketized_force_cpu`: 1,347.57 ms
- validation against exact Python force oracle was enabled
- max relative error: 0.6312

At 8,192 bodies with bucket size 32:

- contribution rows: 1,188,963
- aggregate contribution rows: 341,095
- exact contribution rows: 847,868
- `force_contributions_bucketized_cpu`: 3,133.22 ms
- `bucketized_force_cpu`: 4,294.01 ms
- exact validation skipped because the Python exact oracle is too expensive

These numbers are intentionally not public speedup evidence. They show the
cost of materializing the generic rows in Python and identify the next runtime
target.

## Main Insight

The language shape is now clear:

1. Build or prepare aggregate tree descriptors.
2. Traverse a hierarchical opening frontier.
3. Emit weighted vector contributions for accepted aggregate rows and exact
   fallback rows.
4. Reduce contributions by source into vector sums.

The local Python reference validates the contracts, but it is not the
performance path. The real performance target is to fuse steps 2-4 in a
native or partner-resident path so RTDL avoids materializing millions of Python
rows.

## Remaining Non-Pod Work

Useful local work still possible:

- design a native/partner lowering packet for fused frontier-to-vector-sum;
- add a 3-D version of the reference contract if we decide to align more
  closely with the paper artifact;
- add a memory/row-count estimator to predict when Python row materialization
  becomes unacceptable.

## Pod-Required Work

Requires NVIDIA/OptiX:

- build and run the authors' OWL sample;
- compare RTDL against authors-code timing;
- validate any native OptiX implementation of fused aggregate traversal and
  vector accumulation.

## Claim Boundary

- Not an authors-code comparison.
- Not a paper reproduction.
- Not native timing.
- Not public speedup wording.
- Native engines remain app-name-free; all new contracts use generic weighted
  point, aggregate row, contribution row, and vector-sum vocabulary.
