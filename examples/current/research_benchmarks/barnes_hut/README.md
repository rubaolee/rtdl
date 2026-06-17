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
| `rtdl_barnes_hut_benchmark_app.py` | Research benchmark wrapper around the current Barnes-Hut simulation app |

## First Scope Run

Run from the repository root:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode scope
```

On this Mac, if the default Python lacks `numpy`, use the project virtual
environment:

```bash
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode scope
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
| `aggregate_frontier_collect_bucketized_cpu` | `AGGREGATE_FRONTIER_COLLECT_2D`: generic aggregate-frontier ID collection with source offsets, metadata flags, and row-major i64 rows | App-agnostic CPU-reference row-emission contract for future native/partner lowering; no force law |
| `aggregate_frontier_expanded_membership_cpu` | App-owned Barnes-Hut lowering through `EXPANDED_AABB_POINT_MEMBERSHIP_2D` near-zone candidate rows, then Python opening and force interpretation | Same-contract CPU reference for the RT-assisted lowering |
| `aggregate_frontier_expanded_membership_embree` | Same lowering with Embree-backed generic near-zone candidate rows | CPU RT backend parity for the lowering |
| `aggregate_frontier_expanded_membership_optix` | Same lowering with OptiX-backed generic near-zone candidate rows | RT-core candidate-discovery subpath; force math remains app or partner code |
| `aggregate_frontier_weighted_vector_cpu_host` | Generic aggregate-frontier collection plus streamed host weighted-vector accumulation | Logical CPU baseline for the prepared OptiX app route; materializes frontier rows on host |
| `aggregate_frontier_weighted_vector_embree_host` | Embree-backed aggregate-frontier collection plus streamed host weighted-vector accumulation | Logical Embree baseline for the prepared OptiX app route; materializes frontier rows on host |
| `aggregate_frontier_weighted_vector_cpu_host_numba` | Generic aggregate-frontier collection plus Numba CPU weighted-vector accumulation over row offsets | Optimized no-C++ CPU continuation baseline; still materializes frontier rows on host |
| `aggregate_frontier_weighted_vector_embree_host_numba` | Embree-backed aggregate-frontier collection plus Numba CPU weighted-vector accumulation over row offsets | Optimized no-C++ Embree continuation baseline; still materializes frontier rows on host |
| `force_contributions_bucketized_cpu` | Generic weighted inverse-square vector contribution rows from accepted aggregate and fallback exact rows | App-agnostic force contribution pressure point |
| `bucketized_force_cpu` | Python Barnes-Hut force interpretation over generic bucketized tree/frontier/contribution/vector-sum rows | Full local app behavior without claiming native acceleration |
| `streamed_force_sum_bucketized_cpu` | Generic weighted inverse-square vector sums without materializing contribution rows | Local precursor to native/partner fused frontier-to-vector-sum lowering |
| `materialization_pressure_bucketized_cpu` | Estimate contribution-row memory pressure from the opening frontier summary | Planning guard for materialized vs streamed/native execution |
| `fused_frontier_force_sum_bucketized_cpu` | Generic aggregate-tree opening traversal fused directly into weighted vector sums | Reference contract for native/partner fused lowering; avoids frontier and contribution rows |
| `fused_frontier_force_sum_bucketized_cpu_numba` | Numba CPU aggregate-tree opening traversal fused directly into weighted vector sums | Strongest measured CPU fused baseline; avoids frontier and contribution rows, but is not RT-core evidence |
| `fused_frontier_force_sum_bucketized_numba_cuda` | App front-door route for the reusable Numba CUDA aggregate-tree fused weighted-vector partner API | Current no-C++ fused GPU partner route; avoids frontier and contribution rows, but is not RT-core evidence |
| `prepared_aggregate_frontier_weighted_vector_optix` | Prepared RTDL/OptiX aggregate-frontier device columns plus explicit CuPy or Numba weighted-vector continuation | Current device-resident app route; no frontier/contribution host rows; no automatic partner selection or public speedup claim |
| `optix_node_coverage_prepared` | Prepared OptiX fixed-radius threshold traversal for node coverage | RT-core decision subpath |
| `partner_exact_force` | Generic weighted-point pairwise inverse-square force via CuPy or Numba CUDA JIT | Partner force-vector reference |

## Example Commands

CPU correctness:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode cpu_reference
```

Node-coverage oracle:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode node_coverage_cpu_oracle --body-count 1024
```

Embree candidate rows:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode embree_rows --body-count 4096
```

Generic opening rows:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode opening_rows_cpu
```

Bucketized tree and hierarchical frontier:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode bucketized_tree_cpu --body-count 2048 --bucket-size 32
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode opening_frontier_bucketized_cpu --body-count 2048 --bucket-size 32
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode aggregate_frontier_collect_bucketized_cpu --body-count 2048 --bucket-size 32
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode aggregate_frontier_expanded_membership_embree --body-count 2048 --bucket-size 32
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode aggregate_frontier_expanded_membership_optix --body-count 2048 --bucket-size 32 --require-rt-core
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode force_contributions_bucketized_cpu --body-count 2048 --bucket-size 32
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode bucketized_force_cpu --body-count 2048 --bucket-size 32
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode streamed_force_sum_bucketized_cpu --body-count 2048 --bucket-size 32
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode materialization_pressure_bucketized_cpu --body-count 8192 --bucket-size 32
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode fused_frontier_force_sum_bucketized_cpu --body-count 8192 --bucket-size 32
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode fused_frontier_force_sum_bucketized_cpu_numba --body-count 8192 --bucket-size 64 --theta 0.5 --skip-validation --warmup 2 --repeat 11 --force-output-mode force_summary
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode fused_frontier_force_sum_bucketized_numba_cuda --body-count 8192 --bucket-size 64 --theta 0.5 --skip-validation --warmup 2 --repeat 11 --force-output-mode force_summary
```

Host-materialized logical CPU/Embree baselines for the prepared aggregate-frontier
route:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode aggregate_frontier_weighted_vector_cpu_host --body-count 8192 --bucket-size 64 --theta 0.5 --skip-validation --force-output-mode force_summary
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode aggregate_frontier_weighted_vector_embree_host --body-count 8192 --bucket-size 64 --theta 0.5 --skip-validation --force-output-mode force_summary
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode aggregate_frontier_weighted_vector_cpu_host_numba --body-count 8192 --bucket-size 64 --theta 0.5 --skip-validation --warmup 1 --repeat 5 --force-output-mode force_summary
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode aggregate_frontier_weighted_vector_embree_host_numba --body-count 8192 --bucket-size 64 --theta 0.5 --skip-validation --warmup 1 --repeat 5 --force-output-mode force_summary
```

Prepared OptiX aggregate-frontier device columns plus explicit partner
continuation on an NVIDIA machine:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode prepared_aggregate_frontier_weighted_vector_optix --partner numba --body-count 8192 --bucket-size 64 --theta 0.5 --repeat 5 --warmup 1 --skip-validation --force-output-mode force_summary
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode prepared_aggregate_frontier_weighted_vector_optix --partner cupy --body-count 8192 --bucket-size 64 --theta 0.5 --repeat 5 --warmup 1 --skip-validation --force-output-mode force_summary
```

Local multithreaded exact-force CPU baseline:

```bash
PYTHONPATH=src:. python scripts/goal2532_barnes_hut_multithreaded_cpu_baseline.py --body-count 2048 --thread-counts 1,4
```

Same-contract multithreaded Barnes-Hut C++ baseline:

```bash
PYTHONPATH=src:. python scripts/goal2539_barnes_hut_same_contract_cpp_baseline.py --body-count 8192 --thread-counts 1,4,16
```

No-C++ Numba CUDA fused-subtree prototype on an NVIDIA machine:

```bash
PYTHONPATH=src:. python scripts/v3_0_m52_barnes_hut_numba_cuda_fused_subtree.py --body-counts 8192,16384,32768 --repeat 11 --warmup 2 --output docs/reports/goal4448_v3_0_m52_barnes_hut_numba_cuda_fused_subtree_scale_r11_2026-06-16.json
```

Current force-summary front-door rerank:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so python scripts/v3_0_m62_barnes_hut_current_route_rerank.py --body-counts 8192,16384,32768 --repeat 31 --warmup 3 --output docs/reports/goal4458_v3_0_m62_barnes_hut_current_route_rerank_2026-06-16.json
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so python scripts/v3_0_m62_barnes_hut_current_route_rerank.py --body-counts 65536,131072 --repeat 11 --warmup 2 --output docs/reports/goal4483_v3_0_m87_barnes_hut_large_scale_rerank_2026-06-16.json
```

Reusable no-C++ fused partner API:

```python
prepared = rt.prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda(
    source_points,
    target_points,
    tree_nodes,
)
actual = prepared.sum(theta=0.5, softening=0.05)
```

Goal4450 wires that reusable API into the app front door as
`fused_frontier_force_sum_bucketized_numba_cuda`. Use the app mode for benchmark
evidence and the direct API when embedding the same generic aggregate-tree fused
weighted-vector contract in a custom program.

Older Torch/CUDA fused vector-sum prototypes on an NVIDIA machine:

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
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode optix_node_coverage_prepared --body-count 1000000 --require-rt-core
```

Partner exact force reference:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode partner_exact_force --partner cupy --body-count 4096 --skip-validation
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py --mode partner_exact_force --partner numba --body-count 4096 --skip-validation
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
- generic aggregate-frontier ID collection with fail-closed capacity semantics
  and source-offset plus row-major i64 layout for partner/native consumers;
- generic expanded AABB / point membership rows used as an RT-assisted
  near-zone candidate filter for aggregate-frontier lowering;
- generic aggregate-frontier partner-column adapter for Torch/CuPy downstream
  code, still without native RT traversal or force-law ownership;
- generic weighted inverse-square vector contribution rows;
- generic grouped vector-sum rows;
- generic streamed weighted inverse-square vector sums that avoid
  contribution-row materialization;
- generic vector-sum materialization-pressure estimates;
- generic fused aggregate-frontier weighted vector sums that avoid both
  opening-frontier and contribution-row materialization;
- generic aggregate-tree fused Numba CUDA weighted-vector sums exposed both as a
  reusable API and as the `fused_frontier_force_sum_bucketized_numba_cuda` app
  mode;
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
- Current partner force evidence is exact all-pairs force-vector reference.
  Users can choose CuPy, Torch, or Numba CUDA JIT; the Numba path is the
  no-RawKernel reference for users who want custom CUDA logic in Python. This
  is not hierarchical Barnes-Hut acceleration and not an RT-core claim.
- Current aggregate-frontier collection evidence includes CPU reference,
  partner-ready row layout, app-name-free Embree native row collection, and an
  app-name-free OptiX native row collector with pod parity and host-side timing
  evidence. This is still row collection evidence, not RT-core speedup evidence.
  Default frontier rows are ID-only; distance/opening-ratio diagnostics are an
  explicit debug side channel, not primitive output.
- Current V3 M45/M52/M53/M54/M62/M87 route guidance separates fused baselines from RT evidence.
  `fused_frontier_force_sum_bucketized_cpu_numba` is the strongest measured CPU
  fused baseline. `scripts/v3_0_m52_barnes_hut_numba_cuda_fused_subtree.py`
  provides the scale evidence,
  `prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda` is the reusable
  no-C++ fused GPU partner API, and
  `fused_frontier_force_sum_bucketized_numba_cuda` is the app front-door wrapper
  over that API. The fused Numba CUDA route beats the prepared RTDL/OptiX+Numba
  aggregate-frontier route at the measured 8192/16384/32768 scales. Goal4458
  reranks the current app front doors and keeps fused CPU/Numba as the fastest
  measured force-summary route on the RTX 4000 Ada pod at 8192/16384/32768
  bodies. Goal4483 extends that rerank to 65536/131072 bodies and shows fused
  Numba CUDA is fastest at those larger tested rows, while prepared
  RTDL/OptiX+Numba remains OptiX-library CUDA device-column evidence rather than the
  fastest route. Neither fused route is an Embree implementation or evidence
  that RT cores accelerate Barnes-Hut. The prepared RTDL/OptiX
  aggregate-frontier route remains useful device-column evidence and a
  same-contract partner comparison target.
- Goal4512 closes Barnes-Hut as a current V3 route-policy target, not an
  RT-core acceleration success. Use fused CPU/Numba for the tested
  8192/16384/32768 rows, fused Numba CUDA for the tested 65536/131072 rows, and
  prepared RTDL/OptiX+Numba only when the purpose is OptiX-library CUDA
  aggregate-frontier device-column evidence. A real RT-core Barnes-Hut win still requires the
  future app-agnostic
  `generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1` primitive
  from Goal4497. M113 is not the current Barnes-Hut path; the missing piece is
  fused weighted-vector RT-native accumulation without aggregate-frontier row
  emission, not a prepared graph chunk executor.
- Goal4541 closes Barnes-Hut as a current mixed-explicit route-classification
  target after the Goal4512 policy audit and Goal4527 semantic gate. This means
  there is no immediate V3 app implementation blocker and no next pod action for
  the current route. It does not mean RT-native Barnes-Hut traversal exists, and
  it does not authorize an RT-core speedup claim.
- Goal4517 specifies the future app-agnostic fused RT-native contract as
  `generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1`. It is a
  contract and implementation gate only: no backend symbols, RT-core speedup
  claim, automatic partner dispatch, or paper-reproduction claim are authorized
  until the OptiX implementation matches the CPU and Numba CUDA oracles.
- Goal4518 audits the current prepared aggregate-frontier device-column
  implementation boundary: it is CUDA-kernel device work inside the OptiX
  library, not an `optixLaunch`/`optixTrace` traversal. It remains useful
  device-resident evidence, but it must not be called RT-core traversal
  evidence.
- Goal4523 turns the next RT-native work into an auditable native-symbol gap:
  the generic fused weighted-vector contract exists, and OptiX traversal
  machinery exists elsewhere in the backend, but the required aggregate-tree
  fused prepare/run/destroy symbols and Python wrappers are still absent. The
  next implementation surfaces are `src/rtdsl/optix_runtime.py`,
  `src/native/optix/rtdl_optix_api.cpp`,
  `src/native/optix/rtdl_optix_workloads.cpp`, and
  `src/native/optix/rtdl_optix_core.cpp`.
- Goal4525 removes the Python-wrapper part of that gap: RTDL now exposes an
  app-agnostic OptiX prepared-handle wrapper for
  `AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_RT_NATIVE` output columns. The
  native C++/OptiX prepare/run/destroy symbols and optixTrace traversal proof
  are still absent, so execution and RT-core speedup wording remain blocked.
- Goal4526 removes the missing-symbol cliff by adding the native
  prepare/run/destroy ABI and matching prelude output struct, but the symbols
  intentionally fail closed until a real optixLaunch/optixTrace traversal,
  equivalence oracle, and timing split exist. This is a build-surface step, not
  Barnes-Hut RT-core acceleration evidence.
- Goal4527 blocks a naive replacement of that fail-closed ABI with an all-node
  OptiX any-hit route. Barnes-Hut opening accepts a parent aggregate and must
  suppress its descendants; a single custom-primitive GAS reports node AABBs
  independently, so that direct mapping can double count unless a reviewed
  generic hierarchical traversal/skip design exists. Goal4541 records that
  reviewed hierarchical traversal lowering as future optional research/claim
  expansion rather than a current V3 app implementation blocker.
- Current expanded-membership lowering evidence routes Barnes-Hut
  aggregate-frontier discovery through `EXPANDED_AABB_POINT_MEMBERSHIP_2D`
  near-zone candidate rows. The engine still only sees points, boxes, IDs, and
  rows; Python applies theta/opening logic and force interpretation. This is an
  RT-assisted subpath, not a whole Barnes-Hut speedup claim.
- The aggregate-frontier row schema includes reserved `metadata_flags`, which
  is currently always `0`; partners must ignore unknown future non-zero flags
  unless a later contract revision defines them.
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

Goal2642 adds RTDL-native Embree-vs-OptiX evidence for the Goal2641
expanded-membership aggregate-frontier lowering:

| Bodies | Frontier rows | Embree total | OptiX total | OptiX total speedup | OptiX membership speedup |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 128 | 4,543 | `0.095 s` | `0.707 s` | `0.13x` | `0.06x` |
| 512 | 28,988 | `0.395 s` | `0.282 s` | `1.40x` | `9.09x` |
| 2,048 | 258,495 | `3.556 s` | `1.844 s` | `1.93x` | `30.74x` |
| 8,192 | 1,188,963 | `74.924 s` | `11.191 s` | `6.70x` | `74.68x` |

Interpretation: OptiX loses only at tiny scale where setup dominates. At useful
scales, RT wins the generic membership subpath strongly, while total app
speedup is capped by Python continuation and force interpretation.

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
partner-resident fused vector-sum prototype for the same generic contract.
Goal2638 adds `AGGREGATE_FRONTIER_COLLECT_2D`, an app-independent frontier-ID
collection contract that keeps force math out of the engine while giving
future native/partner lowering a clean row layout. The remaining hard work is
to stabilize that partner path, measure resident-state
reuse across timesteps, and later retry NVIDIA/OptiX paper-code comparison
when an OptiX SDK environment is available. Goal2641 lowers Barnes-Hut
aggregate-frontier discovery onto `EXPANDED_AABB_POINT_MEMBERSHIP_2D` by using
generic near-zone candidate rows and app-owned Python opening/force
interpretation; this is the first RT-assisted aggregate-frontier subpath that
does not add Barnes-Hut-specific native engine logic. Goal2542 replaces the prototype's
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
