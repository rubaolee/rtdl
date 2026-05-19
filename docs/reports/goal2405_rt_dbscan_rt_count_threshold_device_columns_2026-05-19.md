# Goal2405 RT-DBSCAN RT Count-Threshold Device Columns

Date: 2026-05-19

Status: implemented and pod-validated as a generic RTDL v2.x primitive slice

## Purpose

Goal2404 corrected an important claim boundary: the existing
`optix_core_flags_cupy_grid_components_3d` path uses the OptiX backend's
prepared uniform-cell CUDA fixed-radius summaries, not OptiX RT traversal.
Goal2405 adds the missing true-RT slice without adding DBSCAN-specific native
ABI.

The new primitive is:

```text
prepared 3-D fixed-radius count-threshold device columns
```

It prepares a generic 3-D search scene, traces query points through an OptiX
custom-primitive BVH, and writes caller-owned partner/CUDA columns:

```text
query_ids
neighbor_counts       # threshold-capped, not full degree
threshold_flags       # count >= threshold
```

The native names are fixed-radius/count-threshold names only. DBSCAN remains a
Python RTDL+partner composition over this generic primitive plus a generic CuPy
radius-graph component continuation.

## Implementation

- Native OptiX core:
  `kFixedRadiusCountThreshold3DRtKernelSrc`
  with `__raygen__frn3d_count_threshold_probe`,
  `__intersection__frn3d_count_threshold_isect`, and
  `__anyhit__frn3d_count_threshold_anyhit`.
- Native C ABI:
  `rtdl_optix_prepare_fixed_radius_count_threshold_3d`,
  `rtdl_optix_write_prepared_fixed_radius_count_threshold_3d_device_outputs`,
  and `rtdl_optix_destroy_prepared_fixed_radius_count_threshold_3d`.
- Python runtime:
  `prepare_optix_fixed_radius_count_threshold_3d` and
  `PreparedOptixFixedRadiusCountThreshold3D.write_device_count_threshold_columns`.
- Partner adapter:
  `fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns`.
- RT-DBSCAN app mode:
  `optix_rt_core_flags_cupy_grid_components_3d`.

## Pod Environment

Artifacts:

```text
docs/reports/goal2405_rt_dbscan_rt_count_threshold_device_columns_pod/
```

The pod validation used:

```text
root@69.30.85.177 -p 22055
NVIDIA RTX A5000, driver 570.211.01
OptiX SDK v8.1.0
base checkout 61bc82dd05dc83cf48aaabc3b302a80e64dc7159 plus the Goal2405 patch
```

The OptiX backend was built successfully with CUDA 12 selected:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12
```

## Correctness

All pod repeat artifacts report `signatures_match=true`: the new RT-core path
matches the pure CuPy device-grid DBSCAN composition signature on the measured
datasets and sizes.

The local and pod static gates passed:

```text
tests.goal2403_rt_dbscan_repeat_probe_test
tests.goal2405_rt_dbscan_rt_count_threshold_device_columns_test
tests.goal2404_rt_dbscan_optix_backend_claim_boundary_correction_test
```

## Performance Evidence

The following values are application seconds. Repeats include cold first-call
setup; the larger rows show the warm tail separately.

### 4096 Points, Repeat 4

| Dataset | Pure CuPy median | Previous OptiX-backend summary bridge median | New OptiX RT count-threshold median | Result |
| --- | ---: | ---: | ---: | --- |
| clustered3d | 0.019616 | 0.055904 | 0.036032 | New RT path beats prior bridge, not pure CuPy |
| road3d | 0.011064 | 0.041653 | 0.029908 | New RT path beats prior bridge, not pure CuPy |

### Scale Probe

| Dataset | Points | Pure CuPy steady seconds | New OptiX RT steady seconds | RT threshold phase seconds | CuPy continuation seconds | Result |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| clustered3d | 32,768 | 0.178334 | 0.235138 | 0.095040 | 0.059709 | Slower |
| clustered3d | 65,536 | 0.535942 | 0.512446 | 0.212801 | 0.181284 | Slightly faster |
| clustered3d | 131,072 | 1.629228 | 1.257002 | 0.461706 | 0.588995 | Faster |
| road3d | 32,768 | 0.082089 | 0.209449 | 0.099719 | 0.023497 | Slower |
| road3d | 65,536 | 0.278801 | 0.495171 | 0.250561 | 0.087813 | Slower |
| road3d | 131,072 | 0.705156 | 0.967873 | 0.453752 | 0.299664 | Slower |

## Interpretation

Goal2405 proves that RTDL can expose a true OptiX RT traversal count-threshold
primitive and hand its output directly to partner-owned device columns. This is
the first clean RT-DBSCAN slice after the Goal2404 claim correction.

The dense clustered row is the success case: at 131k points, the RT threshold
phase plus CuPy continuation beats the pure CuPy device-grid full app by roughly
1.30x in steady state. The sparse road-like rows remain slower, because the
partner grid baseline is already cheap and the app still performs a separate
CuPy radius-graph component continuation.

The next performance problem is now precise and generic:

```text
device-resident radius-graph component continuation that can consume the RT
traversal stream without redoing candidate-pair traversal
```

That should still not be a DBSCAN-native ABI. It should be a reusable fixed-
radius graph/component continuation primitive or row-stream continuation
contract.

## Claim Boundary

Goal2405 is `accept-with-boundary`.

- Accept: the new path uses true OptiX RT traversal for the threshold/count
  phase, writes partner CUDA columns directly, preserves signatures, and wins on
  the dense clustered 131k scale probe.
- Boundary: this is not RT-DBSCAN paper reproduction, not a broad RT-core DBSCAN
  speedup claim, and not true zero-copy for the full input path because query
  points are still uploaded from host-packed RTDL points.
- Remaining work: make the radius-graph component continuation device-resident
  enough to avoid redoing the same neighbor search after RT thresholding.

## External Review

Gemini independently reviewed Goal2405 in:

```text
docs/reviews/goal2406_gemini_review_goal2405_rt_dbscan_rt_count_threshold_2026-05-19.md
```

The review verdict is `accept-with-boundary`. It accepts the generic primitive
boundary and true RT traversal claim for the threshold/count phase, and agrees
that the next work should be a generic device-resident radius-graph
continuation rather than a DBSCAN-specific native path.
