# Goal4100 - Unordered Non-Skip Partition Stream Evidence

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4093 added an explicit `device_count_then_emit_non_skip` partition-pair stream that elides safe-skip rows but still emits the remaining pairs in sorted `(left, right)` order. Goal4096 moved partition-key decoding onto the device and removed a host reconstruction bottleneck.

Goal4100 tests the next narrow question: if a caller's continuation is order-insensitive, can the non-skip stream skip the final sort and emit rows through device atomic append order?

The new explicit mode is:

`device_count_then_emit_non_skip_unordered`

It records:

- `pair_stream_filter = non_skip_actionable_pairs`
- `safe_skip_pairs_elided = true`
- `pair_order = device_atomic_append_unordered`

This is not the same ordered stream contract as `device_count_then_emit_non_skip`. It is only suitable for continuations that consume partition pairs as an unordered set.

## Pod Setup

Artifacts were generated on an RTX 4000 Ada pod.

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `9e11c05812e7508a83a9f0061a9964df9599e053`
- Point count: 65,536
- Cell factor: 0.125
- Pair mode: `device_count_then_emit_non_skip_unordered`

Artifacts:

- `docs/reports/goal4100_unordered_non_skip_build_pod.json`
- `docs/reports/goal4100_unordered_non_skip_reuse_pod.json`
- `docs/reports/goal4100_unordered_non_skip_phase_pod.json`

## Build Timing Versus Goal4096 Sorted Non-Skip

| Profile | Goal4096 sorted non-skip build median (s) | Goal4100 unordered non-skip build median (s) | Speedup |
| --- | ---: | ---: | ---: |
| clustered3d | 0.076903 | 0.065708 | 1.170x |
| road3d | 0.067624 | 0.057619 | 1.174x |
| ngsim_dense | 0.136991 | 0.121038 | 1.132x |

The result is a real localized improvement. Removing pair sorting helps all three profiles, with the largest effect on the smaller clustered/road rows and a still useful win on the denser NGSIM-shaped row.

## Phase Timing Versus Goal4096 Sorted Non-Skip

| Profile | Goal4096 emit median (s) | Goal4100 unordered emit median (s) | Emit speedup | Goal4096 phase build median (s) | Goal4100 phase build median (s) | Build speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| clustered3d | 0.025104 | 0.010826 | 2.319x | 0.075677 | 0.060787 | 1.245x |
| road3d | 0.018274 | 0.009292 | 1.967x | 0.066259 | 0.056373 | 1.175x |
| ngsim_dense | 0.055287 | 0.040222 | 1.375x | 0.136108 | 0.120157 | 1.133x |

The phase breakdown confirms the mechanism: the unordered mode primarily attacks the emit/sort path. The remaining cost is still distributed across the count pass, cell/partition build work, and component-signature continuation.

## Prepared Reuse Versus Current Recommended Route

| Profile | Goal4096 sorted prepare (s) | Goal4100 unordered prepare (s) | Prepare speedup | Goal4100 5-run speedup vs current route | Goal4100 break-even |
| --- | ---: | ---: | ---: | ---: | --- |
| clustered3d | 0.304351 | 0.292903 | 1.039x | 0.851x | 6.941 runs |
| road3d | 0.097043 | 0.087760 | 1.106x | 0.605x | none |

Prepared setup also improves, but it still does not promote the partition-convergence preview to the default RT-DBSCAN route. The established RTDL/OptiX grouped stream plus Numba continuation remains the recommended route for the current benchmark packet.

## Design Interpretation

Goal4100 is useful because it separates two contracts that were previously coupled:

- Ordered non-skip stream: safer for order-sensitive consumers.
- Unordered non-skip stream: faster for set-like continuations such as component convergence, provided the caller explicitly accepts unordered output.

This is exactly the kind of app-agnostic primitive/routing option the runtime should expose: the engine does not learn DBSCAN, and the user or benchmark adapter explicitly selects the ordering contract.

## Boundary

This report does not promote `partition_convergence_hybrid` as a default route and does not authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, hidden dispatch, automatic partner selection, app-specific engine logic, native ABI additions, or true-zero-copy claims.

Next target remains the larger primitive/runtime issue: avoid the double pass and avoid materializing a full partition-pair table when the continuation can consume device pair status directly.
