# RTDL v2.6 Release Package

Status: released source-tree Python+partner+RTDL boundary.

Version marker: `v2.6`

Release date: 2026-06-02

## Release Statement

RTDL v2.6 is the current source-tree Python+partner+RTDL release. It publishes
the cleaned v2.6 learner documentation surface, the app-agnostic native-engine
boundary, the user-chosen partner guidance for CuPy and Numba continuations, and
the native Embree/OptiX tutorial validation evidence.

The release is source-tree based. Use it from a checkout with
`PYTHONPATH=src:.`. It is not a package-install release, not a broad RT-core
speedup claim, not a whole-application speedup claim, and not a claim that RTDL
optimizes arbitrary PyTorch, CuPy, Numba, or Triton programs.

## What v2.6 Includes

- A single current learner/user documentation surface for v2.6.
- Current tutorials and example commands validated on portable Python plus a
  Linux pod with Embree, OptiX/RT, and CuPy available.
- Primitive-first native RTDL guidance: use fused generic RTDL primitives when
  they exactly express the work.
- Explicit partner choice: users choose the supported partner they want;
  benchmark references may recommend a partner only when same-contract evidence
  supports it.
- CuPy guidance for mature CUDA-array, library, and RawKernel-style
  continuations outside the RTDL primitive.
- Numba guidance for measured custom CUDA-style continuations such as selected
  compact-mask and grouped-reduction rows.
- Triton kept out of recommended paths until same-contract timing shows a win.
- Current benchmark-app and learner-app docs organized so users do not have to
  read old version history unless they enter archive/audit directories.

## Promoted Benchmark App Surface

The v2.6 release keeps the ten benchmark-app portfolio as the design-pressure
suite for RTDL language/runtime work:

| Benchmark app | Directory | Release boundary |
| --- | --- | --- |
| Hausdorff / X-HD-style | `examples/v2_0/research_benchmarks/hausdorff_xhd/` | Bounded exact-distance and RT-assisted evidence; not every input beats CUDA |
| Spatial RayJoin-style | `examples/v2_0/research_benchmarks/spatial_rayjoin/` | Scoped spatial join contracts; not full RayJoin paper reproduction |
| RT-DBSCAN-style | `examples/v2_0/research_benchmarks/rt_dbscan/` | Generic fixed-radius/component benchmark; no DBSCAN-native ABI |
| Robot collision | `examples/v2_0/research_benchmarks/robot_collision/` | Prepared static-scene screening; not a planner or swept solver |
| RayDB-style grouped aggregate | `examples/v2_0/research_benchmarks/raydb_style/` | Fused primitive-first aggregates when they match; not SQL or DBMS |
| Barnes-Hut / RT-BarnesHut-style | `examples/v2_0/research_benchmarks/barnes_hut/` | Aggregate-frontier pressure; force law remains app/partner code |
| LibRTS-style spatial index | `examples/v2_0/research_benchmarks/librts_spatial_index/` | Internal benchmark slice; not full mutable LibRTS reproduction |
| RTNN neighbor search | `examples/v2_0/research_benchmarks/rtnn/` | Prepared ranked-summary rows; not full RTNN paper reproduction |
| Triangle counting | `examples/v2_0/research_benchmarks/triangle_counting/` | Scalar primitive preferred for scalar answer; row interpretation stays app code |
| Bounded contact witness / contact-manifold | `examples/v2_0/research_benchmarks/contact_manifold/` | Bounded witness collection; no contact/manifold native ABI |

## What v2.6 Does Not Claim

- No package metadata, PyPI artifact, or install command is published.
- No universal speedup claim is made for backend flags such as `--backend optix`.
- No arbitrary PyTorch, CuPy, Numba, or Triton acceleration claim is made.
- No automatic partner-selection claim is made.
- No general zero-copy/device-residency product claim is made.
- No whole-application speedup claim is made for the benchmark portfolio.
- No paper-reproduction claim is made unless a specific report says so for a
  specific subpath.

## Minimal Smoke Commands

```bash
PYTHONPATH=src:. python examples/v2_0/getting_started/rtdl_hello_world.py
PYTHONPATH=src:. python examples/v2_0/getting_started/rtdl_feature_quickstart_cookbook.py
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/v2_0/partners/rtdl_partner_anyhit.py --partner numpy --backend embree
```

With a configured NVIDIA pod and OptiX library:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so python examples/v2_0/partners/rtdl_partner_anyhit.py --partner cupy-cuda --backend optix
```

## Evidence

- [v2.6 documentation total audit](../../reports/goal3058_v2_6_release_candidate_doc_total_audit_2026-06-02.md)
- [v2.6 documentation 3-AI consensus](../../reports/goal3061_v2_6_doc_total_audit_3ai_consensus_2026-06-02.md)
- [v2.6 native tutorial/example pod validation](../../reports/goal3062_v2_6_native_tutorial_example_pod_validation_2026-06-02.md)
- [v2.6 native tutorial/example 3-AI consensus](../../reports/goal3065_v2_6_native_tutorial_validation_3ai_consensus_2026-06-02.md)
- [v2.6 release action](../../reports/goal3066_v2_6_release_action_2026-06-02.md)
- [v2.6 final release 3-AI consensus](../../reports/goal3069_final_v2_6_release_3ai_consensus_2026-06-02.md)
- [Partner choice guide](../../learn/partner_choice_for_custom_logic.md)
- [Benchmark partner reference matrix](../../learn/benchmark_partner_reference_matrix.md)
- [Partner acceleration boundaries](../../partner_acceleration_boundaries.md)
- [Current architecture](../../current_architecture.md)

## Release Boundary

RTDL v2.6 is ready as the current public source-tree release for the
Python+partner+RTDL language surface. It makes the learner path cleaner,
validates the curated tutorial commands on native surfaces, and records the
partner-choice boundary. It does not widen performance claims beyond exact
reviewed artifacts.
