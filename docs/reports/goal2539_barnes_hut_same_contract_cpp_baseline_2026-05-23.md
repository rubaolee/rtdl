# Goal2539 Barnes-Hut Same-Contract C++ Baseline

Date: 2026-05-23

## Scope

This goal adds a fallback performance baseline for the Barnes-Hut benchmark app
because the authors' OWL/RT-BarnesHut artifact is present but not buildable on
the available pod without an OptiX SDK root.

The new baseline is:

`std_thread_same_contract_barnes_hut_2d`

Implemented by:

`scripts/goal2539_barnes_hut_same_contract_cpp_baseline.py`

It emits and compiles a standalone C++17 program that implements the same
contract as RTDL's fused Python reference:

`generic_bucketized_aggregate_tree_2d_v1 + generic_aggregate_frontier_weighted_vector_sum_2d_v1`

This is not authors' code, not a paper reproduction, not an OptiX timing, and
not public speedup wording.

## Why This Baseline Is Needed

The earlier exact all-pairs `std::thread` CPU baseline is useful, but it has a
different algorithmic contract from the Barnes-Hut approximation path.

This baseline is stronger for benchmark closeout because it uses:

- the same generated bodies;
- the same bucket size;
- the same `theta`;
- the same `softening`;
- the same bucketized aggregate-tree shape;
- the same aggregate-opening rule;
- the same fused per-source vector accumulation;
- a conventional multithreaded CPU implementation.

It lets us separate:

- RTDL reference Python overhead;
- algorithmic Barnes-Hut work;
- native/partner lowering opportunity.

## Local Evidence

Artifact:

`docs/reports/goal2539_barnes_hut_same_contract_cpp_baseline_local_8192_2026-05-23.json`

Local Mac, 8,192 bodies:

| Threads | Force time (ms) | Contribution rows | Visited nodes |
|---:|---:|---:|---:|
| 1 | 59.78 | 1,188,963 | 509,600 |
| 4 | 14.69 | 1,188,963 | 509,600 |
| 8 | 10.09 | 1,188,963 | 509,600 |

The local fused RTDL Python reference for the same contract recorded 483.92 ms
for 8,192 bodies in Goal2538. This comparison is diagnostic only. It shows
that the remaining performance target is native/partner lowering, not more
Python row plumbing.

## Pod Evidence

Artifact:

`docs/reports/goal2539_barnes_hut_same_contract_cpp_baseline_pod_8192_2026-05-23.json`

Pod:

`root@203.57.40.169:10297`

RTX pod, 8,192 bodies:

| Threads | Force time (ms) | Contribution rows | Visited nodes |
|---:|---:|---:|---:|
| 1 | 62.84 | 1,188,963 | 509,600 |
| 4 | 20.69 | 1,188,963 | 509,600 |
| 16 | 6.01 | 1,188,963 | 509,600 |

The pod fused RTDL Python reference for the same contract recorded 1157.40 ms
for 8,192 bodies in Goal2538. Again, this is a diagnostic engineering
comparison only, not a public speedup claim.

## Correctness Check

The C++ baseline matches the fused RTDL reference contract on:

- contribution row count;
- aggregate contribution count;
- exact contribution count;
- visited node count;
- force checksum within floating-point ordering tolerance.

For 8,192 bodies, both RTDL fused reference and the C++ baseline report:

- contribution rows: `1,188,963`
- aggregate contribution rows: `341,095`
- exact contribution rows: `847,868`
- visited node total: `509,600`

## Claim Boundary

This goal authorizes only these bounded statements:

- RTDL now has a same-contract multithreaded C++ CPU baseline for the
  Barnes-Hut fused reference contract.
- The baseline confirms the fused RTDL Python reference has the same traversal
  and contribution counts.
- The performance gap is an implementation-overhead signal for native/partner
  lowering.

This goal does not authorize:

- RTDL-vs-authors performance claims;
- RTDL-vs-paper reproduction claims;
- public speedup wording;
- OptiX performance claims.

## Next Target

The next real optimization target should be native/partner implementation of:

`generic_aggregate_frontier_weighted_vector_sum_2d_v1`

The C++ baseline defines the CPU-side implementation bar. An OptiX or CUDA
partner implementation must preserve this same contract and report whether tree
state and body state are resident or copied per invocation.
