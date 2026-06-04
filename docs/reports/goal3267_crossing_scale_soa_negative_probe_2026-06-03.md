# Goal3267: Crossing-Scale SoA Negative Probe

Date: 2026-06-03

## Purpose

Goal3266 showed that `crossing_only` is not a legal optimization for the
RayJoin PIP slice because the workload is boundary-heavy. The next inclusive
optimization idea was narrower: keep boundary semantics intact, but precompute
only the crossing-scale term used by the parity branch.

This was intended to avoid the Goal3262 prepared-edge AoS regression, where the
per-edge record doubled memory traffic.

## Probe

The temporary probe added:

- one optional `edge_crossing_scale` pointer in the OptiX PIP launch params,
- one float per prepared edge in a split/SoA buffer,
- an opt-in gate named `RTDL_OPTIX_POINT_PRIMITIVE_USE_CROSSING_SCALE_LAYOUT`,
- and a source-specialized constant so the default path could compile the
  experimental branch away.

The probe preserved inclusive boundary semantics and count validation.

## Pod Evidence

Pod: NVIDIA A40, driver 570.211.01

Probe commit: `914b607c`

Artifacts:

- `docs/reports/goal3267_default_compiletime_same_slice_pod_2026-06-03.json`
- `docs/reports/goal3267_crossing_scale_soa_compiletime_same_slice_pod_2026-06-03.json`
- `docs/reports/goal3267_reverted_control_same_slice_pod_2026-06-03.json`

| Variant | PIP median ms | PIP candidate-count pass median ms | RTDL/RayJoin | Count |
| --- | ---: | ---: | ---: | ---: |
| Default same-commit control | 0.415020 | 0.323024 | 2.136x | 1430 |
| Crossing-scale SoA | 0.372346 | 0.283479 | 1.906x | 1430 |

The SoA path is faster than its same-commit control, but both are slower than
the previously accepted path:

- Goal3264 count-only payload: `0.322377 ms`
- Goal3266 inclusive control before the SoA probe: `0.337990 ms`

The likely reason is that even the narrowed probe increases launch-parameter
surface and kernel pressure enough to erase the saved division work. The result
does not justify keeping the feature in the live engine.

After reverting the live code and rebuilding OptiX, the same-slice control
returned to the accepted range:

| Commit | PIP median ms | PIP candidate-count pass median ms | Count |
| --- | ---: | ---: | ---: |
| `fced1fad` reverted control | 0.339672 | 0.249779 | 1430 |

## Decision

The live code was reverted after measurement:

- `e7020fa6` reverts the compile-time specialization.
- `dd9e4595` reverts the gated crossing-scale SoA probe.
- `fced1fad` records the negative evidence and preserves the reverted live
  source.

This keeps the repository on the faster accepted default while preserving the
negative evidence for future design work.

## Next Direction

This closes another simple per-edge arithmetic path. The remaining plausible
RayJoin PIP directions are larger than scalar precomputation:

- shape-local edge blocking,
- warp-cooperative evaluation for a candidate shape,
- or a richer generic closed-shape membership primitive that exposes a
  device-resident continuation without app-specific RayJoin logic.

## Verification

Local after revert:

`py -3 -m unittest tests.goal3266_crossing_only_boundary_mode_probe_test tests.goal3266_crossing_only_boundary_negative_pod_test tests.goal3264_count_only_intersection_payload_pod_test tests.goal3264_closed_shape_count_only_intersection_payload_test tests.goal3263_prepared_edge_negative_probe_gate_test`

Result: 17 tests passed.

## Boundary

This goal does not authorize release, public speedup wording, broad RT-core
claims, true zero-copy claims, RayJoin paper reproduction claims, or `RTDL beats
RayJoin` claims.
