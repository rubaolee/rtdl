# Goal2534 Barnes-Hut Streamed Vector Sum

Date: 2026-05-23

## Decision

Added a streamed generic vector-sum contract:

- `generic_weighted_inverse_square_vector_sum_2d_v1`

This computes the same weighted inverse-square vector sums as the materialized
contribution-row path, but it does not allocate a Python row for each
contribution. It is still a CPU/Python reference path, not native timing.

## Why

Goal2533 made force contributions generic, but the evidence showed the app was
paying for Python row materialization:

- 2,048 bodies: 258,495 contribution rows
- 8,192 bodies: 1,188,963 contribution rows

That is useful for language clarity, but it is not the performance path. The
runtime design target is fused frontier-to-vector-sum execution.

## What Changed

Implemented in `src/rtdsl/aggregate_tree_reference.py`:

- `sum_weighted_inverse_square_contributions_2d(...)`
- `WEIGHTED_INVERSE_SQUARE_VECTOR_SUM_2D_CONTRACT`

Updated the Barnes-Hut benchmark wrapper:

- added `streamed_force_sum_bucketized_cpu`

The mode still builds the generic bucketized tree and materializes the opening
frontier in Python, but it fuses force contribution and vector summation into a
single streamed generic reference operation.

## Local Evidence

Timing artifact:

- `docs/reports/goal2534_barnes_hut_streamed_vector_sum_local_2026-05-23.json`

At 2,048 bodies:

- materialized `bucketized_force_cpu`: 1,342.59 ms
- streamed `streamed_force_sum_bucketized_cpu`: 1,032.37 ms
- streamed/materialized ratio: 0.769
- checksum delta vs materialized: 0.0 for both x and y

At 8,192 bodies:

- materialized `bucketized_force_cpu`: 3,950.85 ms
- streamed `streamed_force_sum_bucketized_cpu`: 2,660.30 ms
- streamed/materialized ratio: 0.673
- checksum delta vs materialized: 0.0 for both x and y

These are local reference timings only. They do not compare to the authors'
code and do not authorize public speedup wording.

## Main Insight

Avoiding contribution-row materialization already matters in Python. At 8,192
bodies, simply streaming the generic vector sum removes about one third of the
local reference runtime for the force-sum phase while preserving checksums.

The next real engine target is not more Python optimization. It is a native or
partner-resident operation that fuses:

1. hierarchical opening frontier traversal;
2. weighted vector contribution;
3. grouped vector summation;
4. prepared body/tree state reuse.

## Remaining Local Work Before Pod

Useful non-pod work still possible:

- write the formal fused-native lowering packet and ABI sketch;
- add row/memory prediction gates for when Python materialization should be
  rejected or warned;
- decide whether to add 3-D generic reference contracts before native OptiX
  work.

## Pod-Required Work

Requires NVIDIA/OptiX:

- authors' OWL artifact build and timing;
- RTDL native OptiX equivalent timing;
- same-contract validation on large data with RT cores.

## Claim Boundary

- Not an authors-code comparison.
- Not a paper reproduction.
- Not native timing.
- Not public speedup wording.
- Native engine remains app-name-free; all names are generic weighted-point,
  aggregate-frontier, and vector-sum concepts.
