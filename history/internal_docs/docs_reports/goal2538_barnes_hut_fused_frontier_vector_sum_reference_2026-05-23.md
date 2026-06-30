# Goal2538 Barnes-Hut Fused Frontier Vector-Sum Reference

Date: 2026-05-23

## Decision

Add an executable generic reference contract for the Goal2536 fused native
target:

`generic_aggregate_frontier_weighted_vector_sum_2d_v1`

This contract fuses:

- aggregate-tree opening traversal;
- weighted inverse-square contribution evaluation;
- per-source vector accumulation.

It intentionally does not materialize:

- opening-frontier rows;
- weighted contribution rows.

It also intentionally does not add Barnes-Hut vocabulary to native code. The
new function lives in the Python RTDSL reference layer as:

`sum_aggregate_frontier_weighted_vectors_2d(...)`

The benchmark wrapper exposes it as:

`fused_frontier_force_sum_bucketized_cpu`

## Why This Matters

Before this goal, the best non-materialized local path still had two phases:

- build generic opening-frontier rows;
- stream those rows into generic vector sums.

That was already better than materializing contribution rows, but it still
forced the runtime boundary to expose frontier rows as an intermediate table.
The fused reference removes that boundary. Native/partner code can now target
one app-agnostic operation with a direct conformance oracle.

## Contract Semantics

Inputs:

- weighted source points;
- weighted target points;
- prepared aggregate tree rows;
- `theta`;
- `softening`;
- optional fallback-target deduplication.

Outputs:

- one vector-sum row per source;
- `vector_x` and `vector_y`;
- aggregate contribution count;
- exact contribution count;
- total contribution count;
- visited node count.

Metadata records:

- `native_engine_app_specific=false`;
- `intermediate_frontier_rows_materialized=false`;
- `intermediate_contribution_rows_materialized=false`;
- `paper_reproduction=false`;
- `authors_code_comparison=false`;
- `public_speedup_claim_authorized=false`.

Required equivalence:

- The vector sums must match the previous reference composition:
  `evaluate_aggregate_tree_opening_frontier_2d(...)` plus
  `sum_weighted_inverse_square_contributions_2d(...)`.

## Local Diagnostic Timing

Timing artifact:

`docs/reports/goal2538_barnes_hut_fused_frontier_vector_sum_local_2026-05-23.json`

Claim boundary:

`Local Python reference timing only; not native timing, not OptiX timing, not authors-code timing, and not public speedup evidence.`

Local Mac diagnostic results:

| Bodies | Mode | Time (ms) | Intermediate rows avoided |
|---:|---|---:|---|
| 2,048 | `streamed_force_sum_bucketized_cpu` | 993.36 | contribution rows only |
| 2,048 | `fused_frontier_force_sum_bucketized_cpu` | 712.99 | frontier rows and contribution rows |
| 8,192 | `streamed_force_sum_bucketized_cpu` | 2541.72 | contribution rows only |
| 8,192 | `fused_frontier_force_sum_bucketized_cpu` | 483.92 | frontier rows and contribution rows |

The 8,192-body local diagnostic shows why the fused target is the right native
or partner boundary: the reference avoids 1,188,963 contribution rows and
509,600 visited-node frontier materialization events while preserving the same
deterministic vector-sum checksum as the streamed reference.

## Pod Diagnostic Timing

Pod timing artifact:

`docs/reports/goal2538_barnes_hut_fused_frontier_vector_sum_pod_2026-05-23.json`

Pod:

`root@203.57.40.169:10297`

Pod claim boundary:

`Pod Python reference timing only; not native timing, not OptiX timing, not authors-code timing, and not public speedup evidence.`

RTX pod diagnostic results:

| Bodies | Mode | Time (ms) | Intermediate rows avoided |
|---:|---|---:|---|
| 2,048 | `streamed_force_sum_bucketized_cpu` | 2449.22 | contribution rows only |
| 2,048 | `fused_frontier_force_sum_bucketized_cpu` | 1804.98 | frontier rows and contribution rows |
| 8,192 | `streamed_force_sum_bucketized_cpu` | 5741.45 | contribution rows only |
| 8,192 | `fused_frontier_force_sum_bucketized_cpu` | 1157.40 | frontier rows and contribution rows |

Focused pod validation after syncing Goal2538:

- `44 tests OK`

The pod result confirms the fused reference is portable across the local Mac
and the RTX pod Python environment. It still does not imply RT-core execution.

## Claim Boundary

This goal authorizes only bounded engineering statements:

- RTDL now has an executable fused Python reference for aggregate-frontier
  weighted vector sums.
- The fused reference is app-name-free and avoids both frontier-row and
  contribution-row materialization.
- Local and pod Python-reference timings support the implementation direction
  for native/partner lowering.

This goal does not authorize:

- public speedup claims;
- authors-code performance comparisons;
- OptiX performance claims;
- claims that native Embree or OptiX already implement the fused path.

## Next Target

The next implementation target should be one of:

- partner-resident fused vector sum using Torch/CUDA tensor buffers and a
  custom or vectorized kernel path; or
- native OptiX fused traversal once an OptiX SDK environment is available.

The native/partner implementation must use the same contract name and preserve
the app-agnostic metadata boundary.
