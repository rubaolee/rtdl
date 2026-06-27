# Goal2977 RTX 4000 Ada Second-Architecture Packet Attempt

Date: 2026-06-01

Status: **accept-with-boundary / not release-authorizing**

This report records the first v2.5 second-architecture packet attempt on an NVIDIA RTX 4000 Ada Generation pod. It strengthens the cross-GPU evidence for the current v2.5 stack, but it does **not** close the release gate because the canonical 7-app packet did not finish green: six app harnesses passed, while the Barnes-Hut harness was blocked by the 8192-body Embree CPU baseline path running as a single-core bottleneck.

## Pod And Toolchain

| Item | Observed value |
| --- | --- |
| GPU | NVIDIA RTX 4000 Ada Generation |
| Driver | 565.57.01 |
| Compute capability | 8.9 |
| Source commit | `b353be863887fa3b826fc639ea5811d939e93dff` |
| CUDA | 12.4, `nvcc` `/usr/local/cuda-12.4/bin/nvcc` |
| OptiX headers | NVIDIA `optix-dev` tag `v8.1.0`, `OPTIX_VERSION 80100` |
| RTDL OptiX library | `/tmp/rtdl_goal2977_rtx4000ada/build/librtdl_optix.so` |
| Embree | Ubuntu `libembree-dev`, Embree 3.12.2 |
| GEOS | Ubuntu `libgeos-dev`, required by the Embree backend link |
| Python partners | Torch 2.4.1+cu124, Triton 3.0.0, CuPy 14.1.1, Numba 0.65.1 |

Important setup finding: the initial clone of `NVIDIA/optix-dev` main used `OPTIX_VERSION 90100` and failed at runtime with `OptiX error: Unsupported ABI version` on driver 565.57.01. Pinning the headers to `v8.1.0` fixed the ABI mismatch and allowed RTDL/OptiX harnesses to execute.

## Canonical Packet Outcome

Artifact directory:

`docs/reports/goal2977_rtx4000ada_second_arch_packet_pod/`

| Harness | App | Outcome | Notes |
| --- | --- | --- | --- |
| Goal2797 | triangle_counting | pass | OptiX RT path ran; max query median about 0.341 ms. |
| Goal2798 | librts_spatial_index | pass | Tier C no-regression harness ran; max query median about 1.243 ms. |
| Goal2799 | spatial_rayjoin | pass | Prepared OptiX count/parity routes matched CPU references. |
| Goal2800 | rtnn | pass | RTDL/CuPy ratios: uniform 0.983x, clustered 3.291x, shell 4.187x. |
| Goal2801 | hausdorff_xhd | pass | Exact RTDL/OptiX near parity with optimized CuPy grid, ratio 1.003x. |
| Goal2802 | rt_dbscan | pass | Grouped stream speedup vs prepared CuPy grid ranged 3.780x to 4.881x. |
| Goal2803 | barnes_hut | missing in canonical packet | Failed before artifact creation because Embree was initially absent; after installing Embree, the full 8192-body Embree baseline was too slow for a useful immediate rerun. |

Canonical summary:

| Field | Value |
| --- | --- |
| `status` | `fail` |
| `all_pass` | `false` |
| `artifact_count` | 6 |
| `expected_artifact_count` | 7 |
| `source_dirty` | empty |
| `claim_boundary_violations` | empty |

This is a clean partial packet, not a green canonical packet.

## Barnes-Hut Bounded Follow-Up

After installing Embree and GEOS, a bounded Barnes-Hut follow-up ran the same Goal2803 harness with `512:16` and `2048:32` cases only:

`docs/reports/goal2977_rtx4000ada_second_arch_packet_pod/goal2977_barnes_hut_bounded_512_2048.json`

| Bodies | Embree total median sec | OptiX total median sec | OptiX total speedup | OptiX membership speedup | Rows match |
| ---: | ---: | ---: | ---: | ---: | --- |
| 512 | 3.041 | 0.506 | 6.009x | 179.509x | true |
| 2048 | 59.564 | 3.802 | 15.668x | 712.329x | true |

The bounded follow-up confirms that the Barnes-Hut RTDL/OptiX route is correct and RT-core accelerated on RTX 4000 Ada for the smaller and mid-sized rows. The unfinished 8192-body case is not an OptiX failure; it is a CPU-side Embree baseline bottleneck. A killed probe showed the `8192` Embree repeat consuming one CPU core for more than ten minutes without completing the first repeat.

## Interpretation

What improved:

- The v2.5 RTDL/OptiX stack now has real RTX 4000 Ada execution evidence for six canonical app harnesses at the current source commit.
- The OptiX toolchain setup is understood: driver 565 needs OptiX 8.x headers, not OptiX 9.1 headers.
- Barnes-Hut has second-architecture evidence through the bounded 512/2048 cases, including large OptiX membership speedups and backend row parity.

What is still blocked:

- The canonical second-architecture packet is not 7/7 green.
- Barnes-Hut `8192` currently mixes an RTDL/OptiX path with a very slow Embree CPU baseline path. On this pod, that baseline behaves as a single-core bottleneck and makes full second-architecture packet reruns impractical without either a harness policy change or a baseline implementation improvement.
- This report does not authorize a v2.5 release, public speedup wording, broad RT-core wording, true zero-copy wording, paper reproduction claims, package-install claims, or automatic Triton-selection claims.

## Recommended Next Step

Treat this as a release-gap refinement, not a v2.5 failure:

1. Keep the six passing RTX 4000 Ada canonical artifacts and bounded Barnes-Hut evidence as partial second-architecture support.
2. Add a specific Barnes-Hut harness decision before the next release packet:
   - either make the second-architecture packet use a bounded Barnes-Hut CPU-baseline tier, or
   - parallelize/replace the 8192 Embree baseline path so that it can finish predictably on non-A5000 pods.
3. Only after that, rerun a fresh 7/7 second-architecture packet and then request external review.

Verdict: **accept-with-boundary**. The second architecture is materially stronger than before, but v2.5 remains unreleased until the final packet and consensus gates are explicitly closed.
