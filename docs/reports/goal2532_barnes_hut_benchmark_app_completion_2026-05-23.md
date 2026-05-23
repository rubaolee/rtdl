# Goal2532 Barnes-Hut Benchmark App Completion

Date: 2026-05-23

## Decision

Barnes-Hut is now promoted from a scoped research-benchmark scaffold to a
usable RTDL benchmark app lane. The app remains a reconstruction instrument:
it is not a full RT-BarnesHut paper reproduction, not an authors-code timing
comparison, and not public speedup evidence.

The new completed local surface is:

- `generic_bucketized_aggregate_tree_2d_v1`
- `generic_aggregate_tree_opening_frontier_2d_v1`
- `bucketized_force_cpu`, a Python force-law interpretation over the generic
  RTDL tree/frontier rows
- `std_thread_exact_pairwise_force_2d`, a local multithreaded CPU exact-force
  baseline for performance pressure

## Authors' Artifact Intake

The RT-BarnesHut authors' code is available:

- Repository: `https://github.com/vani-nag/OWLRayTracing`
- Branch: `BarnesHutRT`
- Inspected commit: `2a3c60da0bbbd00ff1777cb57ec2089cb0029cf7`
- Inspected path: `samples/cmdline/s01-rtbarneshut`

Local sparse checkout path:

- `scratch/goal2532_owl_barneshut_intake/samples/cmdline/s01-rtbarneshut`

The initially remembered `samples/cmdline/s04-rohan` path was stale; the
branch contains the active sample under `s01-rtbarneshut`.

## Paper-Artifact Optimization Checklist

Adopted locally as app-agnostic RTDL reference contracts:

- Bucketized leaves with default bucket size 32.
- Morton/Z-order sorting before tree construction.
- Bucketized aggregate tree rows with center of mass, mass, member IDs, and
  square half-size.
- DFS-preorder node layout.
- Resume-index metadata, the generic CPU analogue of the artifact's
  `nextPrimId` / `autoRopePrimId` continuation metadata.
- Hierarchical opening-frontier traversal that accepts aggregate rows or falls
  back to exact member rows without revisiting child subtrees after an accepted
  aggregate.

Blocked locally for significant reasons:

- OptiX triangle encoding of tree nodes requires NVIDIA OptiX/OWL and cannot be
  validated on this Mac.
- First-hit RT traversal, closest-hit/miss programs, payload-register behavior,
  and device-side force accumulation require the NVIDIA pod/native path.
- Authors-code timing requires building the OWL sample and running it on an
  NVIDIA machine.
- The current RTDL benchmark app is 2-D. The paper artifact is 3-D; promoting a
  generic 3-D aggregate-tree/frontier primitive is possible later, but it is a
  separate language/runtime design step rather than a local Mac closeout item.

## Implemented Files

- `src/rtdsl/aggregate_tree_reference.py`
- `src/rtdsl/__init__.py`
- `examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py`
- `examples/v2_0/research_benchmarks/barnes_hut/README.md`
- `examples/v2_0/research_benchmarks/README.md`
- `scripts/goal2532_barnes_hut_multithreaded_cpu_baseline.py`
- `docs/reports/goal2532_barnes_hut_multithreaded_cpu_baseline_local_2026-05-23.json`
- `docs/reports/goal2532_barnes_hut_multithreaded_cpu_baseline_local_8192_2026-05-23.json`
- `docs/reports/goal2532_barnes_hut_rtdl_local_timing_2026-05-23.json`
- `docs/reports/goal2532_barnes_hut_rtdl_local_timing_8192_2026-05-23.json`
- `tests/goal2532_barnes_hut_benchmark_app_completion_test.py`

## Local Performance Evidence

These timings are Mac-local diagnostics only. They compare useful local
execution surfaces, but they are not same-contract RT-BarnesHut paper-code
timings and do not authorize speedup wording.

### 2,048 Bodies

| Path | Threads | Time |
| --- | ---: | ---: |
| C++ exact all-pairs CPU baseline | 1 | 15.47 ms |
| C++ exact all-pairs CPU baseline | 4 | 1.81 ms |
| RTDL Python bucketized tree build | n/a | 11.13 ms |
| RTDL Python opening frontier | n/a | 166.41 ms |
| RTDL Python bucketized force + exact validation | n/a | 965.13 ms |

RTDL tree summary at 2,048 bodies:

- `tree_node_count`: 201
- `leaf_node_count`: 151
- `max_depth`: 4
- `max_leaf_member_count`: 32
- `visited_node_total`: 85,512
- `accepted_aggregate_row_count`: 54,264
- `fallback_exact_row_count`: 204,231

### 8,192 Bodies

| Path | Threads | Time |
| --- | ---: | ---: |
| C++ exact all-pairs CPU baseline | 1 | 88.92 ms |
| C++ exact all-pairs CPU baseline | 4 | 20.01 ms |
| RTDL Python bucketized tree build | n/a | 43.88 ms |
| RTDL Python opening frontier | n/a | 1,523.10 ms |
| RTDL Python bucketized force without exact validation | n/a | 1,816.56 ms |

RTDL tree summary at 8,192 bodies:

- `tree_node_count`: 813
- `leaf_node_count`: 610
- `max_depth`: 5
- `max_leaf_member_count`: 32
- `visited_node_total`: 509,600
- `accepted_aggregate_row_count`: 341,095
- `fallback_exact_row_count`: 847,868

## Main Insight

This app exposes a real RTDL runtime/language gap. The tree layout and opening
frontier can be expressed app-agnostically, but the useful performance path is
not Python row materialization. The next serious engine target is native or
partner-resident execution for:

- prepared aggregate-tree descriptors;
- hierarchical opening continuation without Python row expansion;
- vector-valued force contribution and grouped vector-sum reduction;
- device-resident body/tree state reuse across timesteps.

The C++ exact baseline being faster than the Python reference is not a failure
of the benchmark. It is evidence that Barnes-Hut should drive native/partner
runtime reconstruction rather than remain a Python-only demo.

## Claim Boundary

- No public speedup claim.
- No authors-code timing claim.
- No full paper-reproduction claim.
- Current OptiX evidence remains bounded to existing prepared node-coverage
  paths until the OWL/OptiX artifact or an RTDL native equivalent is run on a
  pod.
- Native engines remain app-name-free; Barnes-Hut force semantics stay in
  Python benchmark code until a generic force-contribution primitive is
  designed and reviewed.

## Pod Handoff

A pod is needed only for:

- building/running `OWLRayTracing` branch `BarnesHutRT`, path
  `samples/cmdline/s01-rtbarneshut`;
- collecting authors-code timing if the OWL dependencies can be built;
- validating an RTDL native/OptiX aggregate-tree or force-contribution path.

No pod is needed for the current local benchmark promotion state.
