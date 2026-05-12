# Goal1714 Pod Hardware Validation After Source Recovery

Date: 2026-05-12

Status: pod hardware build and smoke validation follow-up after Goals1708-1711.

## Context

Goal1708 recovered source truncation and stale semantic replay fallout in the
local Windows workspace. Goal1710 restored the Windows toolchain validation
path, and Goal1711 repaired the OptiX source tail and validated the repaired
source on the local Linux smoke host.

This Goal1714 pass used the user-provided pod access to validate the recovered
source on a real NVIDIA pod with current OptiX and Embree builds.

The pod command provided by the user was:

```text
ssh root@157.157.221.29 -p 22464 -i ~/.ssh/id_ed25519
```

The default key path did not authenticate from this Windows machine. The
working local key was:

```text
C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
```

The effective SSH target was:

```text
root@157.157.221.29 -p 22464
```

## Pod Environment

The pod reported:

```text
hostname: 5a955904c650
kernel: Linux 6.8.0-58-generic
GPU: NVIDIA RTX 4000 Ada Generation
driver: 550.163.01
GPU memory: 20475 MiB
CUDA compiler: /usr/local/cuda/bin/nvcc
CUDA version: 12.8, V12.8.93
```

The pod initially lacked required development headers. The validation installed
the available Ubuntu packages:

```bash
apt-get update
apt-get install -y libgeos-dev libembree-dev
```

OptiX headers were also missing initially. The public NVIDIA OptiX SDK was
cloned and pinned to a driver-compatible tag:

```bash
git clone https://github.com/NVIDIA/optix-sdk /root/vendor/optix-sdk
cd /root/vendor/optix-sdk
git checkout v8.0.0
ln -sfn /root/vendor/optix-sdk /opt/optix
```

## Source Sync

The current Windows workspace was copied to the pod as an archive and extracted
to:

```text
/workspace/rtdl_goal1714
```

The protected old tarball was explicitly excluded from the archive:

```text
docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz
```

Extraction was checked with an explicit `extracted_no_goal1204_tarball` marker,
confirming the protected tarball was not copied to the pod workspace.

## Build Validation

Embree build passed on the pod:

```bash
cd /workspace/rtdl_goal1714
make build-embree
```

The build output included:

```text
Embree 4.3.0
build/librtdl_embree.so 393264 bytes
```

OptiX build passed on the pod:

```bash
cd /workspace/rtdl_goal1714
make build-optix OPTIX_PREFIX=/opt/optix CUDA_PREFIX=/usr/local/cuda CUDA_LIB=/usr/local/cuda/targets/x86_64-linux/lib NVCC=/usr/local/cuda/bin/nvcc
```

The build output included:

```text
build/librtdl_optix.so 843984 bytes
```

## Source and Migration Gate

The recovered source and app-agnostic migration gate passed on the pod:

```bash
cd /workspace/rtdl_goal1714
env PATH=/usr/local/cuda/bin:/usr/bin:/bin \
  LD_LIBRARY_PATH=/workspace/rtdl_goal1714/build:/usr/lib/x86_64-linux-gnu:/usr/local/cuda/targets/x86_64-linux/lib:/usr/local/cuda/lib64 \
  PYTHONPATH=src:. \
  /usr/bin/python3 -m unittest \
  tests.goal1711_optix_source_recovery_and_linux_build_validation_test \
  tests.goal1710_windows_toolchain_validation_after_source_recovery_test \
  tests.goal1708_source_recovery_and_semantic_cleanup_test \
  tests.goal1704_legacy_purity_symbol_cleanup_test \
  tests.goal1699_db_to_columnar_payload_native_migration_test \
  tests.goal1697_polygon_to_shape_native_migration_test \
  tests.goal1695_knn_to_k_closest_hits_native_migration_test \
  tests.goal1690_apple_rt_bfs_to_frontier_discover_migration_test \
  tests.goal1688_bfs_to_frontier_edge_traversal_native_migration_test \
  tests.goal1682_hausdorff_to_max_distance_nearest_candidate_native_migration_test \
  tests.goal1681_pip_to_point_primitive_anyhit_native_migration_test \
  tests.goal1673_optix_pose_to_group_native_migration_test \
  tests.goal1672_native_app_leakage_migration_classification_test \
  tests.goal1676_native_leakage_delta_regression_test \
  tests.goal1668_native_engine_app_agnostic_directive_test \
  tests.goal1675_partner_protocol_substrate_test -q
```

Result:

```text
Ran 83 tests in 3.555s
OK (skipped=1)
```

## Runtime Smoke Gate

The Embree and OptiX runtime smoke gate passed on the pod:

```bash
cd /workspace/rtdl_goal1714
env PATH=/usr/local/cuda/bin:/usr/bin:/bin \
  LD_LIBRARY_PATH=/workspace/rtdl_goal1714/build:/usr/lib/x86_64-linux-gnu:/usr/local/cuda/targets/x86_64-linux/lib:/usr/local/cuda/lib64 \
  PYTHONPATH=src:. \
  /usr/bin/python3 -m unittest \
  tests.goal903_embree_graph_ray_traversal_test \
  tests.goal671_optix_prepared_anyhit_count_test \
  tests.goal933_prepared_segment_polygon_optix_test -q
```

Result:

```text
Ran 34 tests in 7.160s
OK (skipped=5)
```

The combined source/migration plus runtime smoke gate also passed:

```text
Ran 117 tests in 5.250s
OK (skipped=6)
```

After this report and its guard test were written, the Goal1714 guard test was
copied back into the same pod workspace and passed there:

```bash
cd /workspace/rtdl_goal1714
env PATH=/usr/local/cuda/bin:/usr/bin:/bin \
  LD_LIBRARY_PATH=/workspace/rtdl_goal1714/build:/usr/lib/x86_64-linux-gnu:/usr/local/cuda/targets/x86_64-linux/lib:/usr/local/cuda/lib64 \
  PYTHONPATH=src:. \
  /usr/bin/python3 -m unittest \
  tests.goal1714_pod_hardware_validation_after_source_recovery_test -q
```

Result:

```text
Ran 4 tests in 0.006s
OK
```

## Goal1659 and Goal1660 Boundary

A follow-up run attempted the v1.6.11 performance manifest tests:

```bash
PYTHONPATH=src:. /usr/bin/python3 -m unittest \
  tests.goal1659_v1_6_11_perf_matrix_test \
  tests.goal1660_v1_6_11_vs_v1_0_perf_matrix_test
```

This was run from the tarball-synced pod workspace, not a git checkout. The
Goal1660 tests failed only because the synced archive did not include `.git`
metadata or the local `v1.0` tag:

```text
ValueError: Goal1660 requires local v1.0 tag
```

That failure is a validation-layout limitation, not evidence of a source,
build, ABI, or pod runtime failure. A full Goal1660 cross-version performance
matrix must be run from a git checkout with the required release tags and
accepted performance artifacts available.

After that limitation was identified, the local `.git` metadata was copied into
the already-validated pod workspace without changing the source tree. The pod
workspace then reported:

```text
git tag --list v1.0
v1.0

git rev-parse HEAD
aee364d677442994958d87dacf3f814360c20ffa
```

With the `v1.0` tag available, the Goal1659/Goal1660 manifest slice passed on
the same pod:

```bash
cd /workspace/rtdl_goal1714
env PATH=/usr/local/cuda/bin:/usr/bin:/bin \
  LD_LIBRARY_PATH=/workspace/rtdl_goal1714/build:/usr/lib/x86_64-linux-gnu:/usr/local/cuda/targets/x86_64-linux/lib:/usr/local/cuda/lib64 \
  PYTHONPATH=src:. \
  /usr/bin/python3 -m unittest \
  tests.goal1659_v1_6_11_perf_matrix_test \
  tests.goal1660_v1_6_11_vs_v1_0_perf_matrix_test -q
```

Result:

```text
Ran 13 tests in 8.654s
OK
```

This validates the v1.6.11/v1.0 manifest preparation and confirms the earlier
failure was caused by the archive sync missing git metadata. It still does not
run the full timed performance matrix rows.

## Verdict

The recovered source passes pod hardware build and runtime smoke validation on
an NVIDIA RTX 4000 Ada pod:

- Embree build: pass.
- OptiX build with OptiX SDK v8.0.0 and CUDA 12.8: pass.
- Source and migration gate: pass, 83 tests with 1 skipped.
- Embree and OptiX runtime smoke gate: pass, 34 tests with 5 skipped.
- Combined gate: pass, 117 tests with 6 skipped.
- Goal1659/Goal1660 tagged manifest gate after restoring `.git` metadata: pass,
  13 tests.

This is accepted pod evidence for source recovery, app-agnostic native migration
integrity, and basic Embree/OptiX runtime viability after the corruption
recovery.

It is not the full v1.6.11 release performance matrix and does not by itself
publish or close v1.8/v2.0 release readiness. The remaining release boundary is
full tagged performance evidence plus final independent release consensus.

Release readiness remains:

```text
needs-more-evidence
```
