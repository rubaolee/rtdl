# Goal2270: Prepared Segment-Pair Count Pod Probe

Status: accepted local evidence pending external review.

## Purpose

Goal2269 added `PreparedOptixSegmentPairIntersection.count(...)` as a generic
exact scalar-count surface for prepared segment-pair intersections. Goal2270
records a clean pushed-commit pod probe that compares:

- `prepared.run_raw(left_segments)`: raw witness-row return from the prepared
  OptiX segment-pair path,
- `prepared.count(left_segments)`: exact scalar count through the new count
  surface,
- same prepared right-side scene,
- same synthetic crossing-grid inputs,
- parity: both paths equal `left_count * right_count`.

This is a focused primitive measurement. It is not a whole RayJoin application claim
and not a RayJoin paper dataset claim.

## Environment

- Commit: `dffabc1317f382dcb19cd3ea30087692a0b69e48`
- Pod: `root@69.30.85.202 -p 22064 -i C:/Users/Lestat/.ssh/id_ed25519_rtdl_codex_current_pod`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- Python: `3.12.3`
- OptiX build: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8`
- Runtime library: `/root/rtdl_goal2198_launcher/rtdl/build/librtdl_optix.so`

## Results

| Left Segments | Right Segments | Intersections | Raw Rows Median Sec | Scalar Count Median Sec | Count / Rows | Rows / Count |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 256 | 256 | 65,536 | 0.006880 | 0.006627 | 0.963x | 1.038x |
| 512 | 512 | 262,144 | 0.026872 | 0.026943 | 1.003x | 0.997x |
| 768 | 768 | 589,824 | 0.076856 | 0.054059 | 0.703x | 1.422x |
| 1,024 | 1,024 | 1,048,576 | 0.129207 | 0.106134 | 0.821x | 1.217x |
| 1,536 | 1,536 | 2,359,296 | 0.266754 | 0.211288 | 0.792x | 1.263x |
| 2,048 | 2,048 | 4,194,304 | 0.492979 | 0.373820 | 0.758x | 1.319x |

All rows reported `parity: true`.

## Interpretation

The count-only surface is not automatically faster at tiny scales, where launch
and refinement overhead dominate. Once witness output becomes large, avoiding
final row allocation and Python witness-row handling becomes useful: the
largest run measured here is about `1.32x` faster than raw witness-row return.

The remaining cost is still dominated by candidate download plus host exact
refinement. This reinforces the same design lesson as Goal2266: v2.0 benefits
from generic count surfaces, but a future version needs a device-resident
output stream or partner-continuation contract to remove more of the candidate
copyback/refinement boundary.

## Claim Boundary

Allowed claim: on this RTX A5000 pod, the generic prepared OptiX segment-pair
exact scalar-count API preserves parity with raw witness rows and becomes faster
than raw witness-row return at larger synthetic crossing-grid sizes.

Not allowed from this evidence:

- whole RayJoin application speedup,
- RayJoin paper dataset reproduction,
- broad RT-core speedup,
- true zero-copy,
- pure device-resident continuation.
