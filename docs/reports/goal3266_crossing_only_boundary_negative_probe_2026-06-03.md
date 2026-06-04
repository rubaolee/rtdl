# Goal3266: Crossing-Only Boundary Negative Probe

Date: 2026-06-03

## Purpose

Goal3265's review confirmed that the remaining RayJoin PIP gap is concentrated
in the closed-shape candidate-count pass, not in any-hit report overhead. A
natural next probe was to ask whether the device-filtered PIP count could skip
explicit point-on-boundary checks and rely only on crossing parity.

This goal adds that experiment as a validation-bound, opt-in mode. It does not
change the default semantics.

## Implementation

- Added a generic `boundary_check` launch parameter to the OptiX closed-shape
  membership PIP kernel.
- Default mode remains inclusive boundary checking for every launch.
- Added `RTDL_OPTIX_POINT_PRIMITIVE_BOUNDARY_MODE`, with `inclusive` as the
  default and `crossing_only` as an opt-in experimental probe.
- Added `device_filtered_boundary_mode` to the RayJoin app and runner.
- The RayJoin app intentionally runs the exact validation count with inclusive
  boundaries, then applies `crossing_only` only to the timed device-filtered
  lane.

This prevents the invalid self-validation failure mode where both the authority
and candidate path use the same approximate predicate.

## Pod Evidence

Pod: NVIDIA A40, driver 570.211.01

Source commit: `65eee5c5`

### Negative Probe

Artifact:

- `docs/reports/goal3266_crossing_only_boundary_negative_probe_pod_2026-06-03.json`

Result:

| Mode | Exact inclusive count | Device-filtered count | Validation |
| --- | ---: | ---: | --- |
| `crossing_only` | 1430 | 129 | fail |

The failure is:

`device-filtered closed-shape count did not match exact prepared count: 129 != 1430`

This means crossing-only is not a legal optimization for this RayJoin PIP slice.
The probe points are boundary-heavy, so inclusive point-on-boundary semantics are
not incidental; they are part of the measured workload contract.

### Inclusive Control

Artifact:

- `docs/reports/goal3266_inclusive_boundary_control_z_point_same_slice_pod_2026-06-03.json`

| Workload | RayJoin median ms | RTDL median ms | RTDL/RayJoin | Count |
| --- | ---: | ---: | ---: | ---: |
| LSI | 0.234191 | 0.454901 | 1.942x | 269 |
| PIP | 0.194407 | 0.337990 | 1.739x | 1430 |

The inclusive control is source-clean and count-preserving, with all claim flags
false. It is slightly slower than Goal3264's best PIP lane (`0.322377 ms`), so
the new launch-parameter plumbing should stay treated as an experiment, not a
new default win.

## Conclusion

Goal3266 closes the crossing-only question negatively:

- The optimization is invalid for the current RayJoin PIP contract.
- The validation path correctly blocks it before any speed claim can be made.
- The generic boundary-mode hook is opt-in and default-inclusive, but it should
  not be used as the next performance path for RayJoin.

The next justified performance target is memory/control reduction inside the
inclusive predicate path, especially shape-local edge blocking or
warp-cooperative edge evaluation that preserves boundary semantics.

## Verification

Local:

`py -3 -m unittest tests.goal3266_crossing_only_boundary_mode_probe_test tests.goal3264_count_only_intersection_payload_pod_test tests.goal3264_closed_shape_count_only_intersection_payload_test tests.goal3263_prepared_edge_negative_probe_gate_test tests.goal3260_rayjoin_runner_records_pip_query_axis_test tests.goal3244_rayjoin_same_slice_repeated_count_runner_test`

Result: 22 tests passed.

Pod:

`python -m unittest tests.goal3266_crossing_only_boundary_mode_probe_test tests.goal3264_count_only_intersection_payload_pod_test tests.goal3264_closed_shape_count_only_intersection_payload_test tests.goal3263_prepared_edge_negative_probe_gate_test`

Result: 14 tests passed.

`make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`

Result: succeeded.

## Boundary

This goal does not authorize release, public speedup wording, broad RT-core
claims, true zero-copy claims, RayJoin paper reproduction claims, or `RTDL beats
RayJoin` claims.
