# Goal2933: Barnes-Hut Explicit CuPy Vector-Sum Selection

Date: 2026-06-01
Status: pod smoke passed

## Purpose

Goal2933 wires the Goal2932 lesson into the Barnes-Hut consolidated harness:
the vector-sum continuation should not choose Torch simply because Triton loses.
It should measure the available same-contract partners and choose the fastest
explicit partner for the generic grouped vector-sum phase.

This keeps the v2.5 rule intact:

- RTDL/native handles generic RT membership/frontier work.
- The partner handles generic grouped vector reduction.
- The app remains responsible for Barnes-Hut meaning and force interpretation.
- No app-specific native engine logic is added.

## Pod Evidence

Artifact:

`docs/reports/goal2933_barnes_hut_cupy_vector_selection_pod/goal2933_barnes_hut_cupy_vector_selection.json`

Pod:

- GPU: `NVIDIA RTX A5000, 570.211.01`
- source commit: `da4507c4214c32c50380ea31bb1414806b6e12ac`
- source dirty: `[]`
- native OptiX library built before the harness run

Command:

```text
python3 scripts/goal2803_barnes_hut_v25_consolidated_harness.py \
  --case 512:16 --repeats 3 --vector-warmups 3 \
  --output /tmp/goal2933_barnes_hut_cupy_selection/goal2933_barnes_hut_cupy_vector_selection.json
```

## Result

The bounded harness passed:

- membership rows match across Embree and OptiX;
- OptiX membership wrapper is RT-core accelerated;
- generic vector sums match Torch reference;
- `cupy` is selected as the fastest measured vector-sum partner for this shape.

| Vector partner | Median seconds | Ratio vs Torch | Selected |
| --- | ---: | ---: | --- |
| Torch scatter-add | `0.000959420` | `1.000x` | no |
| Triton offsets | `0.004002964` | `4.172x` slower | no |
| CuPy by-key | `0.000790042` | `0.823x` | yes |

This is a small but important v2.5 design correction: partner choice is real.
For this continuation, CuPy is the measured fastest same-contract partner on
the RTX A5000 pod, while Triton remains a visible preview and is not promoted.

## Boundary

Goal2933 does not authorize v2.5 release, public speedup wording, broad RT-core
claims, whole-app speedup claims, true zero-copy claims, package-install claims,
automatic Triton selection, automatic CuPy selection, paper-reproduction claims,
or app-specific native engine logic.

The harness now has a better app-level selected partner for this vector-sum
shape, but any public performance wording still requires a separate release
packet and fresh 3-AI release consensus.
