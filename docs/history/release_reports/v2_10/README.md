# RTDL v2.10 Release Package

Status: released source-tree Python+RTDL+partner milestone.

Version marker: `v2.10`

Release date: 2026-06-10

## Release Statement

RTDL v2.10 is the current source-tree milestone for the Python+RTDL+partner
programming model over a generic, app-agnostic native engine. It publishes the
clean current learner path, top-level tutorials, current examples, user-chosen
CuPy/Numba partner guidance, and the ten-app benchmark reference portfolio.

Use RTDL directly from a checkout:

```bash
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
```

This is not a package-install release, not a broad RT-core speedup claim, not a
whole-application speedup claim, not an automatic partner-selection promise,
and not a general zero-copy/device-residency product claim.

## What v2.10 Includes

- A current learner-facing documentation surface centered on `README.md`,
  `docs/`, `tutorials/`, and `examples/current/`.
- Top-level tutorials that teach the current source-tree programming model
  separately from reference docs and runnable examples.
- A ten-app benchmark reference portfolio under
  `examples/current/research_benchmarks/`.
- Primitive-first native RTDL guidance: use a fused generic RTDL primitive when
  it exactly expresses the work.
- Explicit user-chosen partner guidance: CuPy for mature CUDA-array/library
  continuations, and Numba for selected Python-source custom CUDA-style
  continuations.
- Large-scale same-contract CuPy/Numba timing evidence for the partner rows
  where both partners are involved.
- Current claim-boundary scans and public-doc cleanup reports.

## Promoted Benchmark App Surface

| Benchmark app | Directory | v2.10 boundary |
| --- | --- | --- |
| Hausdorff / X-HD-style | `examples/current/research_benchmarks/hausdorff_xhd/` | Exact-distance benchmark and RT-assisted evidence; not every input beats CUDA |
| Spatial RayJoin-style | `examples/current/research_benchmarks/spatial_rayjoin/` | Scoped spatial join contracts; not a full RayJoin paper reproduction |
| RT-DBSCAN-style | `examples/current/research_benchmarks/rt_dbscan/` | Generic fixed-radius/component benchmark; no DBSCAN-native ABI |
| Robot collision | `examples/current/research_benchmarks/robot_collision/` | Prepared static-scene screening; not a full motion planner |
| RayDB-style grouped aggregate | `examples/current/research_benchmarks/raydb_style/` | Fused primitive-first aggregates when they match; not SQL or a DBMS |
| Barnes-Hut / RT-BarnesHut-style | `examples/current/research_benchmarks/barnes_hut/` | Aggregate-frontier pressure; force law remains app/partner code |
| LibRTS-style spatial index | `examples/current/research_benchmarks/librts_spatial_index/` | Benchmark slice for spatial-index pressure; not full mutable LibRTS |
| RTNN neighbor search | `examples/current/research_benchmarks/rtnn/` | Prepared ranked-summary rows; not full RTNN paper reproduction |
| Triangle counting | `examples/current/research_benchmarks/triangle_counting/` | Scalar primitive preferred for scalar answer; row interpretation stays app code |
| Contact witness / contact manifold | `examples/current/research_benchmarks/contact_manifold/` | Bounded witness collection; no contact/manifold native ABI |

## Minimal Smoke Commands

Portable source-tree smoke:

```bash
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
PYTHONPATH=src:. python examples/current/getting_started/rtdl_feature_quickstart_cookbook.py
PYTHONPATH=src:. python examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/current/partners/rtdl_partner_anyhit.py --partner numpy --backend embree
```

With a configured NVIDIA pod and OptiX library:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so python examples/current/partners/rtdl_partner_anyhit.py --partner cupy-cuda --backend optix
```

## Evidence

- [v2.10 milestone release packet](../../../reports/goal4267_v2_10_milestone_release_packet_2026-06-10.md)
- [Claude v2.10 release-packet review](../../../reviews/goal4268_claude_review_goal4267_v2_10_milestone_release_packet_2026-06-10.md)
- [Gemini v2.10 release-packet review](../../../reviews/goal4269_gemini_review_goal4267_v2_10_milestone_release_packet_2026-06-10.md)
- [v2.10 3-AI release consensus](../../../reports/goal4270_v2_10_milestone_release_3ai_consensus_2026-06-10.md)
- [Large-scale CuPy/Numba partner comparison](../../../reports/goal4266_large_scale_cupy_numba_partner_comparison_2026-06-09.md)
- [v2.10 public-doc cleanup](../../../reports/goal4271_v2_10_user_doc_cleanup_audit_2026-06-10.md)
- [Current documentation recheck](../../../reports/goal4274_current_doc_recheck_2026-06-10.md)
- [Top-level tutorial reorganization](../../../reports/goal4276_top_level_tutorial_reorganization_2026-06-10.md)
- [Choosing A Partner For Custom Logic](../../learn/partner_choice_for_custom_logic.md)
- [Benchmark Partner Reference Matrix](../../learn/benchmark_partner_reference_matrix.md)
- [Partner Acceleration Boundaries](../../partner_acceleration_boundaries.md)
- [Current Architecture](../../current_architecture.md)

## Tag And Head Note

The `v2.10` tag exists as the source-tree milestone tag authorized by the
Goal4270 consensus. Later learner-doc cleanup commits on `main` keep the same
v2.10 source-tree surface and should not be interpreted as a wider release
claim or as authorization to move the published tag without an explicit
maintainer decision.

Do not move the existing tag without a separate explicit maintainer decision.

## Release Boundary

RTDL v2.10 is ready as the current public source-tree milestone for the
Python+RTDL+partner language surface. It keeps the engine generic, makes partner
choice explicit, and presents tutorials/docs/examples as separate clean doors.
All performance wording remains evidence-only and path-specific.
