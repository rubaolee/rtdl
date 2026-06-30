# Goal2544 Barnes-Hut Subtree-Containment Optimization

Date: 2026-05-23

## Scope

Goal2544 targets the main bottleneck discovered after the Goal2542
resume-index rope prototype for:

`generic_aggregate_frontier_weighted_vector_sum_2d_v1`

The prior kernel still answered `contains_source` by linearly scanning every
visited node's member list. At 32,768 bodies this dominated the resident CUDA
kernel:

- Goal2542 rope kernel: `37.036 ms`
- authors' OWL/OptiX reported force phase: `6.616 ms`

The goal was to move the RTDL generic implementation as close as possible to
the authors' force-phase timing without adding Barnes-Hut app knowledge to the
engine contract.

## Optimization

Implementation:

`scripts/goal2544_barnes_hut_torch_cuda_subtree_containment.py`

The optimized descriptor adds two generic prepared-tree arrays:

- `node_subtree_end_index`: DFS end index for each node's subtree;
- `source_leaf_node_index`: the DFS leaf containing each source row.

Because the aggregate tree is DFS ordered, and each internal node's member set
is exactly the union of its descendant leaves, source containment is:

`node_index <= source_leaf_node_index[source] < node_subtree_end_index[node]`

This replaces the old per-node member scan with an O(1) range check. The
descriptor is still app-name-free: it describes prepared aggregate-tree
membership, not Barnes-Hut-specific force logic.

## Pod Evidence

Pod:

`ssh root@203.57.40.169 -p 10297 -i ~/.ssh/id_ed25519_rtdl_codex`

Device:

`NVIDIA RTX A5000`, driver `565.57.01`

Artifacts:

- `docs/reports/goal2544_barnes_hut_subtree_containment_pod_8192_2026-05-23.json`
- `docs/reports/goal2544_barnes_hut_subtree_containment_pod_32768_2026-05-23.json`

Focused local/pod test:

`PYTHONPATH=src:. python3 -m unittest tests.goal2544_barnes_hut_subtree_containment_test`

## Correctness

For both 8,192 and 32,768 bodies:

- `visited_node_total` delta: `0`
- `contribution_row_count` delta: `0`
- checksum deltas: floating-point summation noise only

This means the optimized kernel preserves the RTDL reference contract while
removing the linear containment scan.

## Timing

Resident CUDA kernel timings on the RTX A5000 pod:

| Bodies | Goal2542 rope min (ms) | Goal2544 subtree min (ms) | Speedup vs Goal2542 |
|---:|---:|---:|---:|
| 8,192 | 7.035 | 1.045 | 6.73x |
| 32,768 | 37.036 | 3.971 | 9.33x |

Comparison to the authors' reported force phase from Goal2543:

| Bodies | RTDL Goal2544 generic CUDA min (ms) | Authors OWL/OptiX force min (ms) | Boundary |
|---:|---:|---:|---|
| 8,192 | 1.045 | 5.346 | not same contract |
| 32,768 | 3.971 | 6.616 | not same contract |

The numerical result is stronger than the immediate target, but it is not a
public RTDL-vs-authors speedup claim. The contracts differ: RTDL is currently a
generic 2-D weighted-vector-sum prototype, while the authors' sample is the
published OWL/OptiX RT-BarnesHut artifact.

## Engineering Conclusion

The 37 ms bottleneck was primarily not rope traversal itself. It was the
generic containment query implemented as a linear member scan.

The important runtime lesson is that generic prepared aggregate-tree
descriptors need subtree/leaf membership metadata. This should become part of
the next stable partner/native lowering design for hierarchical aggregate
continuations.

Remaining work before stronger claims:

- same-contract RTDL native/partner API surface for the subtree descriptor;
- repeated-timestep resident-state benchmark with prepared tensors reused;
- precision/contract policy for float32 versus float64;
- possible warp/block scheduling for high-work sources;
- external review before any public wording.

## Claim Boundary

Authorized internal statements:

- Goal2544 preserves the RTDL generic fused vector-sum contract on the tested
  sizes.
- Replacing member-list containment scans with DFS subtree containment reduces
  the 32K resident kernel from `37.036 ms` to `3.971 ms` on the A5000 pod.
- This is a generic RTDL runtime descriptor improvement, not Barnes-Hut app
  logic inside the engine.

Not authorized:

- public speedup wording;
- paper reproduction claims;
- same-contract comparison against the authors' OWL/OptiX artifact;
- claims that the OptiX native engine already implements this path.
