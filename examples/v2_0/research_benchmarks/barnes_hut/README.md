# Barnes-Hut / RT-BarnesHut-Style Study

This directory promotes the existing Barnes-Hut force example into a serious
RTDL research benchmark.

The study is informed by:

- Vani Nagarajan, Rohan Gangaraju, Kirshanthan Sundararajah, Artem Pelenitsyn,
  and Milind Kulkarni, "RT-BarnesHut: Accelerating Barnes-Hut Using
  Ray-Tracing Hardware," PPoPP 2025.
- DOI: `10.1145/3710848.3710885`

The goal is not to clone the paper implementation. The goal is to use the app
shape to force RTDL language/runtime reconstruction around hierarchical spatial
aggregation, opening decisions, vector-valued force accumulation, and prepared
state reuse.

## File

| File | Role |
| --- | --- |
| `rtdl_barnes_hut_benchmark_app.py` | Research benchmark wrapper around the existing v2.0 Barnes-Hut simulation app |

## First Scope Run

Run from the repository root:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode scope
```

On this Mac, if the default Python lacks `numpy`, use the project virtual
environment:

```bash
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode scope
```

## Modes

| Mode | Meaning | RTDL role |
| --- | --- | --- |
| `scope` | Report the benchmark scope, paper reference, supported contracts, and non-goals | Documentation guard |
| `cpu_reference` | Existing bounded one-level app: candidate rows plus Python opening rule and force oracle | Correctness/reference |
| `node_coverage_cpu_oracle` | CPU oracle for body-to-tree-node coverage at a fixed radius | Same-contract decision oracle |
| `rtdl_cpu_rows` | Generic fixed-radius body-to-node candidate rows through the CPU RTDL backend | Candidate-row contract |
| `embree_rows` | Same candidate-row contract through Embree | CPU RT backend parity |
| `opening_rows_cpu` | Generic aggregate opening rows: accepted aggregate-node rows plus fallback exact-body rows | First benchmark-specific reconstruction primitive, still app-name-free |
| `bucketized_tree_cpu` | Bucketized Morton-ordered aggregate tree rows with DFS order and resume-index metadata | Portable subset of the paper artifact's tree layout optimizations |
| `opening_frontier_bucketized_cpu` | Hierarchical opening frontier over the bucketized aggregate tree | App-agnostic continuation pressure point before native RT lowering |
| `force_contributions_bucketized_cpu` | Generic weighted inverse-square vector contribution rows from accepted aggregate and fallback exact rows | App-agnostic force contribution pressure point |
| `bucketized_force_cpu` | Python Barnes-Hut force interpretation over generic bucketized tree/frontier/contribution/vector-sum rows | Full local app behavior without claiming native acceleration |
| `streamed_force_sum_bucketized_cpu` | Generic weighted inverse-square vector sums without materializing contribution rows | Local precursor to native/partner fused frontier-to-vector-sum lowering |
| `materialization_pressure_bucketized_cpu` | Estimate contribution-row memory pressure from the opening frontier summary | Planning guard for materialized vs streamed/native execution |
| `fused_frontier_force_sum_bucketized_cpu` | Generic aggregate-tree opening traversal fused directly into weighted vector sums | Reference contract for native/partner fused lowering; avoids frontier and contribution rows |
| `optix_node_coverage_prepared` | Prepared OptiX fixed-radius threshold traversal for node coverage | RT-core decision subpath |
| `partner_exact_force` | Generic weighted-point pairwise inverse-square force via CuPy or Torch | Partner force-vector reference |

## Example Commands

CPU correctness:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode cpu_reference
```

Node-coverage oracle:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode node_coverage_cpu_oracle --body-count 1024
```

Embree candidate rows:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode embree_rows --body-count 4096
```

Generic opening rows:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode opening_rows_cpu
```

Bucketized tree and hierarchical frontier:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode bucketized_tree_cpu --body-count 2048 --bucket-size 32
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode opening_frontier_bucketized_cpu --body-count 2048 --bucket-size 32
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode force_contributions_bucketized_cpu --body-count 2048 --bucket-size 32
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode bucketized_force_cpu --body-count 2048 --bucket-size 32
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode streamed_force_sum_bucketized_cpu --body-count 2048 --bucket-size 32
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode materialization_pressure_bucketized_cpu --body-count 8192 --bucket-size 32
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode fused_frontier_force_sum_bucketized_cpu --body-count 8192 --bucket-size 32
```

Local multithreaded exact-force CPU baseline:

```bash
PYTHONPATH=src:. python scripts/goal2532_barnes_hut_multithreaded_cpu_baseline.py --body-count 2048 --thread-counts 1,4
```

Same-contract multithreaded Barnes-Hut C++ baseline:

```bash
PYTHONPATH=src:. python scripts/goal2539_barnes_hut_same_contract_cpp_baseline.py --body-count 8192 --thread-counts 1,4,16
```

Torch/CUDA fused vector-sum prototype on an NVIDIA machine:

```bash
PYTHONPATH=src:. python scripts/goal2541_barnes_hut_torch_cuda_fused_vector_sum.py --body-count 8192 --repeats 5
PYTHONPATH=src:. python scripts/goal2542_barnes_hut_torch_cuda_rope_vector_sum.py --body-count 8192 --repeats 5
PYTHONPATH=src:. python scripts/goal2544_barnes_hut_torch_cuda_subtree_containment.py --body-count 32768 --repeats 5
PYTHONPATH=src:. python scripts/goal2545_barnes_hut_resident_state_benchmark.py --body-count 32768 --timesteps 100 --warmups 5
PYTHONPATH=src:. python scripts/goal2546_barnes_hut_float32_subtree_kernel.py --body-count 32768 --repeats 20
PYTHONPATH=src:. python scripts/goal2547_barnes_hut_3d_scalar_subtree_kernel.py --body-count 32768 --input-file /path/to/authors_generated_input.txt --theta 0.5 --softening 0.0 --repeats 5
```

OptiX prepared node coverage on an NVIDIA machine:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode optix_node_coverage_prepared --body-count 1000000 --require-rt-core
```

Partner exact force reference:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode partner_exact_force --partner cupy --body-count 4096 --skip-validation
```

## Current Scope

The current promoted benchmark starts from three existing RTDL surfaces:

- body-to-quadtree-node candidate rows;
- prepared fixed-radius node-coverage threshold decisions;
- generic aggregate opening rows that split accepted aggregate nodes from
  fallback exact-body rows;
- generic bucketized aggregate-tree rows using Morton/Z-order sorting,
  bucket-size policy, DFS layout, and resume-index metadata;
- generic hierarchical opening-frontier rows over that tree;
- generic weighted inverse-square vector contribution rows;
- generic grouped vector-sum rows;
- generic streamed weighted inverse-square vector sums that avoid
  contribution-row materialization;
- generic vector-sum materialization-pressure estimates;
- generic fused aggregate-frontier weighted vector sums that avoid both
  opening-frontier and contribution-row materialization;
- generic resident-state aggregate-frontier execution;
- generic 3-D scalar inverse-square aggregate-frontier sums for authors-facing
  contract alignment;
- generic partner exact-force reference over weighted points.

That is enough to start the benchmark-app lane, but it is not the final
RT-BarnesHut reconstruction. The runtime pressure points are:

- hierarchical spatial aggregate descriptors;
- opening-predicate continuation over tree nodes;
- paper-artifact layout policy: bucketized leaves, Morton ordering, DFS node
  order, and autorope-like resume metadata;
- vector-valued force contribution rows;
- grouped vector-sum reductions, especially without Python row
  materialization;
- partner-resident force accumulation;
- prepared tree lifetime versus dynamic body state.

## Claim Boundary

- This is a research benchmark / reconstruction instrument.
- It is not a full RT-BarnesHut paper reproduction.
- It is not an authors-code comparison.
- It is not a public speedup claim.
- The authors' code exists in the `BarnesHutRT` branch of
  `github.com/vani-nag/OWLRayTracing` under `samples/cmdline/s01-rtbarneshut`,
  but timing it requires an NVIDIA/OWL/OptiX-capable machine.
- Current OptiX evidence is bounded to prepared node-coverage threshold
  traversal, not Barnes-Hut opening-rule acceleration.
- Current partner force evidence is exact all-pairs force-vector reference, not
  hierarchical Barnes-Hut acceleration and not an RT-core claim.
- Current 3-D scalar evidence shares the authors' dimensionality, scalar
  inverse-square force shape, and generated input files, but it is not a
  same-tree-contract authors-code comparison.
- Goal2549 rejected a proposed native inverse-square aggregate-frontier scalar
  symbol because hardcoding the force law in the engine violates the
  app-independent native-engine principle.
- Native Embree/OptiX paths must remain app-name-free. Python owns
  Barnes-Hut-specific tree policy, opening semantics, and force interpretation
  until a generic primitive is designed and reviewed.

## Current Performance Snapshot

The strongest current NVIDIA evidence is from an RTX A5000 pod using the
Torch/CUDA partner prototypes. These timings are internal engineering evidence,
not public speedup claims.

| Stage | 32K resident min | Meaning |
| --- | ---: | --- |
| Goal2542 2-D rope float64 | `37.036 ms` | before subtree containment |
| Goal2544 2-D subtree float64 | `3.971 ms` | O(1) source containment |
| Goal2545 2-D resident repeated float64 | `3.565 ms` | prepared-state repeated launch |
| Goal2546 2-D subtree float32 | `0.473 ms` | precision-reduced diagnostic path |
| Goal2547 3-D scalar float32 | `0.509 ms` | same dimension/input/force shape as authors, not same tree |
| Goal2550 3-D scalar float32 final | `0.503 ms` | 20-repeat final run, same RTDL Python-reference contract |
| Authors OWL/OptiX `new` force phase | `5.405 ms` | authors-supported generated-input mode; orientation only |

The main measured optimization was replacing per-node source-membership scans
with generic DFS subtree containment metadata:
`source_leaf_node_index` and `node_subtree_end_index`. The next claim gate is
not more raw kernel tuning; it is aligning the 3-D path with the authors' exact
tree/traversal contract or explicitly reviewing a narrower claim boundary.
No speedup ratio should be inferred from the RTDL and authors timing rows:
both are phase-only orientation numbers under different tree/traversal
contracts, the authors binary segfaulted on direct same-input `treelogy`
reload on the final pod, and RTDL correctness is currently against RTDL's own
3-D Python reference rather than authors' per-body force output.

## Promotion Status

Goal2530 promotes Barnes-Hut into the research-benchmark directory with a
guarded wrapper and docs. Goal2531 adds the first generic reconstruction
primitive, `generic_aggregate_opening_rows_2d_v1`, as a CPU/Python reference
contract. Goal2532 adopts the portable paper-artifact optimizations as
app-agnostic rows: `generic_bucketized_aggregate_tree_2d_v1` and
`generic_aggregate_tree_opening_frontier_2d_v1`. Goal2533 adds
`generic_weighted_inverse_square_contribution_rows_2d_v1` and
`generic_grouped_vector_sum_rows_2d_v1`, moving force-contribution mechanics
out of Barnes-Hut-specific helper code. Goal2534 adds
`generic_weighted_inverse_square_vector_sum_2d_v1`, a streamed local reference
that avoids materializing contribution rows. Goal2535 adds
`generic_vector_sum_materialization_pressure_2d_v1` so the benchmark can state
when materialized Python rows should be replaced by streamed/native execution.
Goal2538 adds `generic_aggregate_frontier_weighted_vector_sum_2d_v1`, a fused
reference that eliminates both frontier-row and contribution-row
materialization. Goal2539 adds a same-contract multithreaded C++ CPU baseline
for that fused path, because the authors' OWL/OptiX artifact requires an OptiX
SDK environment before timing can proceed. Goal2541 adds the first Torch/CUDA
partner-resident fused vector-sum prototype for the same generic contract. The
remaining hard work is to stabilize that partner path, measure resident-state
reuse across timesteps, and later retry NVIDIA/OptiX paper-code comparison
when an OptiX SDK environment is available. Goal2542 replaces the prototype's
explicit per-thread stack with DFS `resume_index` rope traversal; this is
correct and slightly faster, but not the main remaining bottleneck. Goal2544
replaces the per-node `contains_source` member scan with generic DFS subtree
containment metadata (`source_leaf_node_index` and `node_subtree_end_index`),
dropping the 32K A5000 resident kernel from `37.036 ms` to `3.971 ms` while
preserving the generic RTDL reference contract. Goal2545 confirms prepared
state reuse at `3.565 ms` minimum per 32K timestep. Goal2546 shows that a
float32 policy is a major speed lever, reaching `0.473 ms` minimum with small
relative error against the float64 reference. Goal2547 moves the diagnostic
comparison to 3-D scalar inverse-square force on authors-generated input and
reaches `0.509 ms` minimum, but the tree/traversal contract still differs from
the authors' OWL/OptiX artifact. This remains internal engineering evidence,
not same-contract authors-code or public speedup wording. Goal2549 rejected
promoting the same inverse-square scalar math into native `librtdl_optix`,
because that would put workload-specific force accumulation inside the
app-independent engine. Goal2550 closes the app phase with a final 32K A5000
3-D scalar run at `0.503 ms` minimum over 20 repeats and records that the
authors artifact's direct same-input reload path segfaulted, leaving the
authors `new` mode as orientation-only evidence.
