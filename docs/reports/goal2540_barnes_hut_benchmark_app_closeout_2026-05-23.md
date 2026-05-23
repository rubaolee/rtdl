# Goal2540 Barnes-Hut Benchmark App Closeout

Date: 2026-05-23

## Conclusion

The Barnes-Hut / RT-BarnesHut-style app has been promoted to a serious RTDL
research benchmark.

The app is not a full RT-BarnesHut paper reproduction and does not yet have an
OptiX fused traversal backend. Its value is that it forced RTDL to expose and
test new app-agnostic language/runtime contracts for hierarchical spatial
aggregation and vector-valued reductions.

## What Was Added

Benchmark wrapper:

- `examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py`
- `examples/v2_0/research_benchmarks/barnes_hut/README.md`

Generic RTDSL contracts:

- `generic_aggregate_opening_rows_2d_v1`
- `generic_bucketized_aggregate_tree_2d_v1`
- `generic_aggregate_tree_opening_frontier_2d_v1`
- `generic_weighted_inverse_square_contribution_rows_2d_v1`
- `generic_grouped_vector_sum_rows_2d_v1`
- `generic_weighted_inverse_square_vector_sum_2d_v1`
- `generic_vector_sum_materialization_pressure_2d_v1`
- `generic_aggregate_frontier_weighted_vector_sum_2d_v1`

Benchmark/baseline scripts:

- `scripts/goal2532_barnes_hut_multithreaded_cpu_baseline.py`
- `scripts/goal2539_barnes_hut_same_contract_cpp_baseline.py`

## Paper-Informed Optimizations Adopted

The following portable paper-artifact ideas were adopted as app-agnostic RTDL
reference contracts:

- bucketized aggregate-tree leaves;
- Morton/Z-order source ordering;
- DFS node layout;
- resume-index/autorope-like metadata;
- aggregate opening rule over hierarchical tree rows;
- fused frontier traversal plus weighted vector accumulation;
- explicit separation of tree construction, traversal, and vector reduction;
- materialization-pressure guard for frontier/contribution rows.

The following paper-specific or environment-specific pieces were not adopted
inside RTDL v2.x native code in this goal:

- OWL/OptiX triangle encoding of tree nodes;
- first-hit traversal with disabled AnyHit;
- OptiX continuation shader implementation;
- authors-code timing.

Those are not rejected. They are deferred to the native/partner lowering target
because they require either an OptiX SDK environment or a new CUDA/OptiX
implementation path.

## Authors-Code Gate

Authors' artifact:

- repository: `https://github.com/vani-nag/OWLRayTracing`
- branch: `BarnesHutRT`
- commit observed on pod: `2a3c60da0bbbd00ff1777cb57ec2089cb0029cf7`
- sample path: `samples/cmdline/s01-rtbarneshut`

The available pod had CUDA but did not have the OptiX SDK root required by OWL:

`Could NOT find OptiX (missing: OptiX_ROOT_DIR)`

Evidence:

- `docs/reports/goal2537_barnes_hut_authors_code_cmake_configure_pod_2026-05-23.txt`
- `docs/reports/goal2537_barnes_hut_pod_validation_and_authors_code_gate_2026-05-23.md`

Therefore, authors-code performance comparison remains blocked until a pod or
machine provides the NVIDIA OptiX SDK and a valid `OptiX_ROOT_DIR`.

## Performance Evidence

All performance statements here are diagnostic engineering evidence only. They
do not authorize public speedup wording.

### RTDL Python Reference

Goal2538 local Mac, 8,192 bodies:

| Mode | Time (ms) | Boundary |
|---|---:|---|
| `streamed_force_sum_bucketized_cpu` | 2541.72 | avoids contribution rows |
| `fused_frontier_force_sum_bucketized_cpu` | 483.92 | avoids frontier and contribution rows |

Goal2538 RTX pod, 8,192 bodies:

| Mode | Time (ms) | Boundary |
|---|---:|---|
| `streamed_force_sum_bucketized_cpu` | 5741.45 | avoids contribution rows |
| `fused_frontier_force_sum_bucketized_cpu` | 1157.40 | avoids frontier and contribution rows |

### Same-Contract C++ Baseline

Goal2539 local Mac, 8,192 bodies:

| Threads | Force time (ms) |
|---:|---:|
| 1 | 59.78 |
| 4 | 14.69 |
| 8 | 10.09 |

Goal2539 RTX pod, 8,192 bodies:

| Threads | Force time (ms) |
|---:|---:|
| 1 | 62.84 |
| 4 | 20.69 |
| 16 | 6.01 |

The same-contract C++ baseline validates the benchmark contract and gives a
CPU-side implementation bar for future native/partner lowering.

## What This App Taught RTDL

Barnes-Hut adds requirements that earlier benchmark apps did not force:

- hierarchical aggregate descriptors, not just flat primitive sets;
- continuation over a tree using an opening predicate;
- vector-valued reductions, not scalar count/sum/min/max only;
- row-materialization pressure from intermediate frontier and contribution
  tables;
- prepared tree lifetime separate from dynamic source/body state;
- need for fused native/partner execution rather than Python-mediated row
  pipelines.

The most important language/runtime outcome is the fused generic contract:

`generic_aggregate_frontier_weighted_vector_sum_2d_v1`

This is the correct next native/partner target because it expresses the app's
core runtime pressure without app-specific native vocabulary.

## Validation

Local focused suite:

- `51 tests OK`

Pod focused suite:

- `51 tests OK`

The pod used:

`ssh root@203.57.40.169 -p 10297 -i ~/.ssh/id_ed25519_rtdl_codex`

## Claim Boundary

Allowed statements:

- Barnes-Hut is now a promoted RTDL research benchmark app.
- The benchmark has app-agnostic Python reference contracts for aggregate-tree
  opening, vector contribution, streamed vector sum, materialization-pressure
  estimation, and fused frontier-to-vector-sum execution.
- The authors' artifact was found and gated; timing is blocked by missing
  OptiX SDK root in the available pod.
- A same-contract multithreaded C++ CPU baseline exists for diagnostic
  comparison.

Disallowed statements:

- RTDL reproduces the RT-BarnesHut paper.
- RTDL outperforms the authors' implementation.
- RTDL has OptiX fused Barnes-Hut traversal performance evidence.
- RTDL has public Barnes-Hut speedup wording.

## Next Work

The benchmark-promotion phase can stop here.

The next real optimization phase should be a new goal focused on one native or
partner implementation of:

`generic_aggregate_frontier_weighted_vector_sum_2d_v1`

Reasonable first targets:

- Torch/CUDA partner-resident fused traversal over prepared tree arrays;
- CUDA extension prototype using the C++ baseline as the CPU conformance oracle;
- OptiX fused traversal once an OptiX SDK machine is available.
