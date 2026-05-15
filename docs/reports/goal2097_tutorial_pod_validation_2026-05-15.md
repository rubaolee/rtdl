# Goal2097 Tutorial Pod Validation

Date: 2026-05-15

## Purpose

Validate the current v2.0-facing tutorial programs on a real NVIDIA pod, with
both Embree and OptiX/RT coverage wherever the tutorial surface exposes those
backends.

## Pod And Environment

| Item | Value |
| --- | --- |
| SSH target | `root@213.173.99.11 -p 19564` |
| Accepted key on this Windows machine | `~/.ssh/id_ed25519_rtdl_codex_current_pod` |
| GPU | NVIDIA RTX 2000 Ada Generation |
| Driver | `570.195.03` |
| CUDA used for build/runtime | `/usr/local/cuda-12` |
| OptiX SDK | `/root/vendor/optix-sdk`, linked as `/opt/optix` |
| RTDL checkout | `/root/rtdl_tutorial_validation` |
| Validated commit | `6f2219d2febcf24538fbc448771f330813e6199c` |
| Embree library | `build/librtdl_embree.so` |
| OptiX library | `build/librtdl_optix.so` |
| OptiX CUDA runtime link | `libnvrtc.so.12` |

## Issues Found And Fixed

| Issue | Fix |
| --- | --- |
| `examples/rtdl_fixed_radius_neighbors.py --backend optix` was documented as a tutorial progression but the CLI only allowed CPU/Embree choices. | Added `optix` CLI support and dispatch through `rt.run_optix`. |
| `examples/rtdl_knn_rows.py --backend optix` had the same tutorial/CLI mismatch. | Added `optix` CLI support and dispatch through `rt.run_optix`. |
| `examples/rtdl_partner_anyhit.py --partner numpy --backend optix` failed when no partner framework had initialized CUDA first. | `src/rtdsl/optix_runtime.py` now initializes the CUDA driver and sets the primary device-0 context before loading/running OptiX. |

## Result

The committed-code rerun passed all tutorial matrix rows:

| Measure | Value |
| --- | ---: |
| Total commands | 41 |
| Passed | 41 |
| Failed | 0 |
| Timed out | 0 |
| Timeout per command | 90 seconds |

Detailed artifacts:

- [Markdown result table](goal2097_tutorial_pod_validation/goal2097_tutorial_matrix_results.md)
- [JSON result artifact](goal2097_tutorial_pod_validation/goal2097_tutorial_matrix_results.json)

## Scope Boundary

This validates tutorial correctness and backend availability on the provided
pod. It is not a broad performance claim and does not by itself authorize final
v2.0 release. The final v2.0 release still requires the strict 3-AI consensus gate.
