# Goal3831: Robot-Collision Probe-Reference Separation For Scale Profiles

Date: 2026-06-07

Status: implemented and A5000-validated.

## Purpose

Goal3830 showed that RT-DBSCAN's large row was not an execution timeout once
CPU validation was separated from the performance row. Goal3831 applies the
same discipline to the robot-collision benchmark.

The previous scale row,
`robot_collision_optix_scale_default_1024`, spent most of its wall time in a
CPU probe-reference pass over the 1024-pose / 128-obstacle fixture. The
prepared OptiX device-count repeats were already tiny:

- median repeated `total_run_seconds`: about `0.00007s`;
- median native `traversal`: about `0.000043s`;
- one-time prepared-scene build: about `0.134s`;
- one-time prepared-query build: about `0.197s`.

The runner-level `11.309s` value was therefore a validation-inclusive benchmark wall time, not a hot-path OptiX timing.

## Implementation

`examples/v2_0/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py`
now accepts:

```bash
--no-probe-reference
```

for prepared repeated modes. The default remains unchanged: probe-reference
validation still runs unless the flag is explicitly supplied.

When the flag is used, the output records:

- `reuse_metadata.probe_reference_validated = false`;
- `reuse_metadata.probe_reference_seconds = null`;
- `probe_reference_compact_link_flags = null`;
- `probe_reference_signature = null`;
- per-run `matches_probe_reference = null`;
- aggregate match fields as `null`.

That prevents a performance-only row from masquerading as a correctness row.

## Registry Update

The current ten-app scale-profile registry now uses:

`robot_collision_optix_scale_default_1024_no_probe_reference`

with the same 1024-pose / 128-obstacle / 4-link shape and the explicit
`--no-probe-reference` flag.

## Correctness Boundary

This does not weaken correctness requirements. Smaller correctness rows and the
default prepared benchmark modes still use the CPU probe reference. Goal3831
only changes the large default scale-profile command so it measures prepared
OptiX execution without CPU reference validation dominating the timing.

## A5000 Evidence

Fresh A5000 rerun:

```bash
PYTHONPATH=.pydeps_goal3788_numba:src:. \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
RTDL_EMBREE_LIBRARY=$PWD/build/librtdl_embree.so \
python scripts/goal3828_current_benchmark_scale_profile_runner.py \
  --heartbeat-sec 10 \
  --stdout-tail 12000 \
  --output-json docs/reports/goal3828_current_benchmark_scale_profiles_a5000/summary.json
```

Artifact:

`docs/reports/goal3828_current_benchmark_scale_profiles_a5000/summary.json`

Result: all ten scale rows passed. The robot row:

| Field | Value |
| --- | --- |
| row id | `robot_collision_optix_scale_default_1024_no_probe_reference` |
| runner wall time | `1.552s` |
| stdout bytes | `8886` |
| `app_lowering_seconds` | `0.568s` |
| `prepare_build` | `0.128s` |
| `prepared_query_build` | `0.211s` |
| median repeated `total_run_seconds` | `0.0000758s` |
| median native `traversal` | `0.0000446s` |
| `probe_reference_validated` | `false` |
| forbidden true claim flags | none |

The earlier validation-inclusive default row was `11.309s` on the same A5000
scale runner. The corrected performance row is therefore about `7.3x` lower in
runner wall time while still reporting that the probe reference was not run.

## Boundary

Goal3831 does not authorize release action, package-install wording, public
speedup wording, whole-app acceleration wording, broad RT-core wording,
paper-reproduction wording, true-zero-copy wording, AMD performance wording,
automatic partner selection, or app-specific native-engine logic.

It is a scale-profile calibration cleanup only.
