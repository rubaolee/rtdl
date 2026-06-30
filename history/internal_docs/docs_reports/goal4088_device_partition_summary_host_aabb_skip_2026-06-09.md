# Goal4088 Device Partition-Summary Host AABB Skip

Date: 2026-06-09

## Verdict

`accept-with-boundary`

Goal4088 removes a generic waste path from the partition-convergence preview:
when pair enumeration is device-backed (`device_bounded_offsets` or
`device_count_then_emit`), the builder no longer rebuilds partition AABBs on the
host. The device AABB columns already exist and are the columns consumed by the
device pair-status kernels.

This is a real runtime improvement, not an app-specific trick. It does not
promote the partition-convergence route as the default.

## What Changed

In `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`,
`build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(...)`
now builds the host `key_to_ordinal` map and host-side AABB dictionaries only
inside the `pair_enumeration == "host"` branch.

For device enumeration paths, it still builds the occupied partition key rows
needed by the existing device pair-status kernels, but it skips the unused
`cupy.asnumpy(point_partition_ids)` transfer and Python AABB accumulation loop.

## Pod Evidence

Artifacts:

- `docs/reports/goal4088_partition_summary_build_after_host_aabb_skip_pod.json`
- `docs/reports/goal4088_partition_summary_build_after_host_aabb_skip_pod.stdout.txt`
- `docs/reports/goal4088_partition_reuse_after_host_aabb_skip_pod.json`
- `docs/reports/goal4088_partition_reuse_after_host_aabb_skip_pod.stdout.txt`

Hardware:

- NVIDIA RTX 4000 Ada Generation, driver 550.127.05

Source commit:

- `b5cb796894bfb02bfd16cd5f15776220631f0ce7`

## Build-Time Result

All pair counts and status counts match the Goal4085 baseline.

| Profile | Goal4085 median sec | Goal4088 median sec | Improvement |
| --- | ---: | ---: | ---: |
| `clustered3d` | 0.219861 | 0.103282 | 2.129x |
| `road3d` | 0.201510 | 0.088037 | 2.289x |
| `ngsim_dense` | 0.367637 | 0.223795 | 1.643x |

The skipped host work was therefore material. It was not the whole problem:
the device pair-status path still materializes complete visible pair streams
with 10M-30M partition-pair rows at 65K.

## Reuse-Threshold Result

The prepared-reuse threshold improves but remains narrow:

| Profile | Prepare sec | Replay median sec | Current route reference sec | 5-run speedup vs current reference | Break-even runs |
| --- | ---: | ---: | ---: | ---: | ---: |
| `clustered3d` | 0.336437 | 0.053635 | 0.093321 | 0.772x | 8.48 |
| `road3d` | 0.117964 | 0.040972 | 0.036245 | 0.561x | never |

Clustered repeated signatures become more plausible: the break-even point drops
from roughly 11.04 runs to 8.48 runs. Road still does not break even because
replay remains slower than the current grouped-stream route.

## Policy

This optimization should be kept. It improves a generic preview path and removes
unnecessary host work.

It should not change the current recommended route. The next real performance
step remains a cheaper native/device producer or fused safe-full/ambiguous work
stream that avoids full visible partition-pair materialization.

## Boundary

This report does not promote `partition_convergence_hybrid`, add a native ABI,
change default routing, authorize release wording, public speedup wording, broad
RT-core wording, whole-app acceleration wording, paper-reproduction wording,
hidden dispatch, automatic partner selection, app-specific engine logic, or true
zero-copy wording.
