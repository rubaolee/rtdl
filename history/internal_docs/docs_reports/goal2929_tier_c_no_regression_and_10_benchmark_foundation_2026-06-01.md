# Goal2929: Tier C No-Regression And 10-Benchmark Foundation

Date: 2026-06-01
Status: pod smoke passed

## Purpose

Goal2929 strengthens the v2.5 ten-benchmark foundation after Goal2925 refreshed
the seven-app canonical packet. The seven-app packet covers the current Tier A/B
performance harnesses, while the manifest still listed two Tier C apps using
historical evidence:

- `contact_manifold`
- `robot_collision`

Goal2929 adds fresh RTX A5000 no-regression smoke for those two Tier C apps and
updates the v2.5 benchmark manifest so all ten benchmark apps now have current
or explicitly indexed evidence.

Artifact directory:

`docs/reports/goal2929_tier_c_no_regression_pod/`

## Pod Evidence

Pod:

- GPU: `NVIDIA RTX A5000, 570.211.01`
- source commit: `1ec2cf9efe23eb2c4067671b394cc32d52c64e11`
- source dirty: `[]`
- CUDA home: `/usr/local/cuda-12`
- OptiX SDK: `/root/vendor/optix-sdk`
- PTX arch/compiler: `compute_86`, `nvcc`

Commands:

```text
python3 examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py \
  --mode aabb_broadphase_collect_k --dataset grid --grid-count 512 \
  --witness-capacity 512 --backend optix --discovery-backend optix \
  --discovery-warmup 2 --discovery-repeat 5

python3 examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py \
  --backend optix --optix-summary-mode prepared_pose_flags --output-mode pose_flags \
  --pose-count 512 --obstacle-count 256

python3 examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py \
  --backend optix --optix-summary-mode prepared_pose_flags --output-mode pose_flags \
  --pose-count 65536 --obstacle-count 1024 --skip-validation
```

## Results

| App | Artifact | Result | Boundary |
| --- | --- | --- | --- |
| `contact_manifold` | `contact_manifold_grid512_optix.json` | `matches_cpu_reference = true`; OptiX generic AABB broadphase median `0.003084s`; exact Python refinement retained | Tier C no-regression, not public speedup |
| `robot_collision` | `robot_pose_flags_512_256_validation.json` | `matches_oracle = true`; prepared OptiX pose-flags path active | Tier C correctness/no-regression |
| `robot_collision` | `robot_pose_flags_65536_1024_timing_skip_validation.json` | 65,536 poses timing smoke; validation explicitly skipped for timing scale | timing-only companion, not correctness proof |

The 65,536-pose timing artifact is compacted: it stores pose-flag counts,
checksums, and samples rather than the full per-pose flag array. The smaller
512-pose validation artifact carries the correctness proof.

The contact path remains generic:

- RTDL sees `AABB_INDEX_QUERY_2D` candidate discovery and
  `COLLECT_K_BOUNDED` witness row collection.
- Contact/collision meaning stays in the Python benchmark.
- No native contact/manifold ABI or app-specific engine logic is introduced.

The robot path remains bounded:

- RTDL sees prepared generic ray/triangle any-hit pose flags.
- The app's robot semantics remain at the Python wrapper level.
- The timing artifact is not a full robot-planning, kinematics, CCD, or
  witness-row claim.

## 10-Benchmark Position

Current v2.5 benchmark foundation:

| Tier | Apps | Evidence |
| --- | --- | --- |
| A | `raydb_style`, `triangle_counting`, `spatial_rayjoin` | Goal2896 plus Goal2925 current packet |
| B | `rt_dbscan`, `rtnn`, `barnes_hut`, `hausdorff_xhd` | Goal2925 current packet |
| C | `librts_spatial_index`, `contact_manifold`, `robot_collision` | Goal2925 for `librts`; Goal2929 for contact/robot |

This makes the ten-app foundation easier to explain: seven apps are in the
canonical performance packet, RayDB is tracked through its same-contract gate,
and the two remaining Tier C apps now have fresh no-regression smoke.

## Boundary

Goal2929 does not authorize v2.5 release, public speedup wording, broad RT-core
claims, whole-app speedup claims, true-zero-copy claims, automatic
Triton-selection claims, package-install claims, or paper-reproduction claims.

The Tier C rows are intentionally no-regression evidence. They should not be
promoted into partner-parity or public performance rows unless the user
explicitly asks to turn either app into a Tier A/B benchmark campaign.
