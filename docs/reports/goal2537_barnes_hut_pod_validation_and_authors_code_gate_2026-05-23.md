# Goal2537 Barnes-Hut Pod Validation And Authors-Code Gate

Date: 2026-05-23

## Scope

This goal uses the provided RTX pod to validate the Barnes-Hut benchmark app
slice outside the local Mac environment, collect diagnostic CPU/Python timings,
and check whether the published OWL/RT-BarnesHut artifact can be built for a
same-artifact comparison.

This is not an RTDL public speedup packet. The evidence here is a gate report:

- RTDL reference correctness and diagnostic timings on the pod;
- local exact `std::thread` CPU baseline timing on the pod;
- authors-code build feasibility for the available pod environment;
- next native/partner implementation target.

## Pod Access And Environment

The user-provided command used key path `~/.ssh/id_ed25519`, but that file was
not present on this Mac. The working RTDL key was:

`~/.ssh/id_ed25519_rtdl_codex`

The successful pod access command was:

`ssh root@203.57.40.169 -p 10297 -i ~/.ssh/id_ed25519_rtdl_codex`

Observed pod environment:

- host: `05cd7c946142`
- OS/kernel: Ubuntu/Linux, kernel `6.8.0-48-generic`
- GPU: NVIDIA RTX A5000, 24 GB
- driver: `565.57.01`
- CUDA runtime reported by `nvidia-smi`: `12.7`
- CUDA toolkit: `/usr/local/cuda-12.8`
- `nvcc`: `12.8.93`
- `cmake`: `3.28.3`
- `g++`: `13.3.0`
- Python: `3.12.3`
- Python packages observed: `numpy 2.1.2`, `torch 2.8.0+cu128`

The pod initially lacked GEOS development headers/libraries required by the
existing native oracle tests. I installed:

`apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq libgeos-dev pkg-config`

## Validation Result

The local working tree was staged to `/root/rtdl_python_only` on the pod because
the latest Barnes-Hut work was not yet available from Git.

Focused suite:

`tests.goal504_barnes_hut_force_app_test`
`tests.goal2530_barnes_hut_benchmark_app_promotion_test`
`tests.goal2531_barnes_hut_generic_opening_rows_test`
`tests.goal2532_barnes_hut_benchmark_app_completion_test`
`tests.goal2533_barnes_hut_generic_force_contributions_test`
`tests.goal2534_barnes_hut_streamed_vector_sum_test`
`tests.goal2535_barnes_hut_materialization_pressure_test`
`tests.goal2536_barnes_hut_fused_native_lowering_packet_test`

Command shape:

`cd /root/rtdl_python_only && export PATH=/usr/local/cuda-12.8/bin:/usr/local/cuda/bin:$PATH && PYTHONPATH=src:. python3 -m unittest ...`

Result after installing GEOS:

- `35 tests OK`

## Pod Diagnostic Timing

The pod CPU/Python timing artifact is:

`docs/reports/goal2537_barnes_hut_pod_rtdl_reference_timing_2026-05-23.json`

Claim boundary in that artifact:

`Pod CPU/Python reference timing only; not OptiX timing, not authors-code timing, and not public speedup evidence.`

Diagnostic timing summary:

| Bodies | Mode | Time (ms) | Contribution rows | Notes |
|---:|---|---:|---:|---|
| 2,048 | `bucketized_force_cpu` | 3267.46 | 258,495 | materialized contribution rows |
| 2,048 | `streamed_force_sum_bucketized_cpu` | 2545.80 | 258,495 | no materialized contribution rows |
| 2,048 | `materialization_pressure_bucketized_cpu` | 267.26 | 258,495 | recommends `materialized_reference_allowed` |
| 8,192 | `bucketized_force_cpu` | 9523.33 | 1,188,963 | materialized contribution rows |
| 8,192 | `streamed_force_sum_bucketized_cpu` | 5951.03 | 1,188,963 | no materialized contribution rows |
| 8,192 | `materialization_pressure_bucketized_cpu` | 2552.71 | 1,188,963 | recommends `streamed_or_native_fused` |

At 8,192 bodies, the streamed vector-sum reference avoids the 1,188,963-row
Python contribution table and preserves the same deterministic vector-sum
contract as the materialized reference. The timing JSON records diagnostic
checksums, but those numbers are not used here as a public correctness claim.

## Exact CPU Baseline

The pod exact all-pairs baseline artifact is:

`docs/reports/goal2537_barnes_hut_pod_cpu_baseline_8192_2026-05-23.json`

Claim boundary in that artifact:

`Local exact O(N^2) std::thread CPU baseline only. It is useful for sanity/performance pressure, but it is not RT-BarnesHut paper-code timing and not a whole-app RTDL speedup claim.`

Diagnostic timing summary for 8,192 bodies:

| Baseline | Threads | Time (ms) |
|---|---:|---:|
| exact all-pairs `std::thread` CPU | 1 | 312.55 |
| exact all-pairs `std::thread` CPU | 4 | 82.09 |
| exact all-pairs `std::thread` CPU | 16 | 21.53 |

This baseline intentionally uses a different algorithmic contract from the
Barnes-Hut approximation path. It is a pressure baseline and sanity reference,
not an authors-code comparison.

## Authors-Code Gate

Authors' artifact:

- repository: `https://github.com/vani-nag/OWLRayTracing`
- branch: `BarnesHutRT`
- commit observed on pod: `2a3c60da0bbbd00ff1777cb57ec2089cb0029cf7`
- sample path: `samples/cmdline/s01-rtbarneshut`

The configure log is preserved at:

`docs/reports/goal2537_barnes_hut_authors_code_cmake_configure_pod_2026-05-23.txt`

Configure command shape:

`cmake -S . -B build-rtdl-bh -DCMAKE_BUILD_TYPE=Release -DBUILD_SAMPLES=ON -DBUILD_TESTING=OFF`

Result:

`Could NOT find OptiX (missing: OptiX_ROOT_DIR)`

Conclusion:

The authors-code timing comparison is blocked in this pod because the CUDA
toolkit is present but the NVIDIA OptiX SDK root is not available to OWL CMake.
Do not report authors-code timing from this pod. A valid authors-code comparison
requires an environment with the OptiX SDK installed and `OptiX_ROOT_DIR`
configured.

## Engineering Conclusion

The Barnes-Hut benchmark slice is now validated on a CUDA-capable pod at the
Python/reference-contract layer, but the remaining high-value performance work
is not another Python-mode timing run.

The next engine target remains the Goal2536 fused generic operation:

`generic_aggregate_frontier_weighted_vector_sum_2d_v1`

That target should fuse:

- aggregate-tree opening traversal;
- weighted inverse-square vector contribution;
- grouped vector accumulation;
- direct output of per-source vector sums;
- no Python frontier/contribution-row materialization;
- no Barnes-Hut app name or app-specific ABI in native code.

The authors-code comparison should be retried only after OptiX SDK availability
is confirmed on a pod.

## Release/Claim Boundary

This report supports three bounded statements:

- The Barnes-Hut reference contracts pass the focused suite on an RTX A5000 pod.
- The current Python materialized path has clear row-materialization pressure at
  8,192 bodies, and the streamed Python reference avoids the contribution table.
- The available pod cannot build the authors' OWL/RT-BarnesHut artifact because
  `OptiX_ROOT_DIR` is missing.

This report does not authorize:

- RTDL-vs-authors speedup claims;
- OptiX backend performance claims for this app;
- whole-app public performance claims;
- claims that the current native engine already implements the fused
  Barnes-Hut-style traversal.
