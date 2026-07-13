# Goal5119 - X-HD Phase Semantics And Author Contract

Date: 2026-07-08

## Verdict

```text
completed_xhd_phase_semantics_author_directed_hd_contract
```

## Purpose

Define the comparison contract before any performance matrix:

- what the author `HDResult` means;
- what the author `Running.AvgTime` measures;
- what it excludes;
- which RTDL value may be compared to it.

This goal is semantic/accounting only. It does not add a new X-HD route and does
not claim performance parity.

## Source Evidence

The checked author source is the POD checkout used for the build gate:

```text
/tmp/xhd-goal5112/author
commit: 7bf41c8442d059c94f4178355c6d5a10571d9658
binary: /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
```

Relevant source facts:

```text
src/main.cpp: variant == "rt" -> Variant::kRT
src/run_hausdorff_distance.cu: repeat loop calls CalculateDistance(...)
src/run_hausdorff_distance.cu: running_time += repeat_stats["ReportedTime"]
src/run_hausdorff_distance.cu: json_run["AvgTime"] = running_time / repeat
src/run_hausdorff_distance.cu: stats.Log("HDResult", dist)
src/hd_impl/hausdorff_distance_rt.h: stats["Algorithm"] = "XHD"
src/hd_impl/hausdorff_distance_rt.h: stats["Execution"] = "GPU"
src/hd_impl/hausdorff_distance_rt.h: stats["ReportedTime"] = sw_total.ms()
```

## Author Metric Semantics

`HDResult` is the distance returned by the selected implementation for
`input1 -> input2`. In the `rt/gpu` path, that implementation initializes work
over `points_a` and searches `points_b`; it is the directed Hausdorff distance
from input1 to input2.

Therefore the paper app comparator must compare author `HDResult` to:

```text
directed_a_to_b
```

not to the symmetric max unless a future author-source audit proves the author
binary is running a symmetric two-direction wrapper for that invocation.

The current bounded fixtures happen to have:

```text
directed_a_to_b == symmetric max == 1.0 or 2.0
```

so older summaries were numerically unaffected, but the contract is now explicit
in both author-gate and RTDL-route summaries:

```text
author_comparison_reference = directed_a_to_b
```

## Performance Phase Semantics

The author `Running.AvgTime` is:

```text
mean(repeat_stats["ReportedTime"] for each repeat)
```

where `ReportedTime` is the X-HD implementation timer inside
`CalculateDistanceImpl`.

It includes the measured X-HD internal algorithm work for the repeat, including
recorded fields such as:

```text
BVHBuildTime
Iterations[*].RTTime
Iterations[*].CUDATime
Iterations[*].AdjustBVHTime when present
```

It does not represent the whole process wall clock. It excludes or sits below
the broader process envelope that includes:

```text
process startup
input file parsing/loading
host-to-device point conversion
RT engine construction before the repeat loop
JSON writing
shell/python wrapper overhead
```

This distinction is mandatory for future performance claims.

## Current Bounded Author Phase Values

From the existing POD author JSONs:

| Fixture | Dimensions | HDResult | Running.AvgTime |
| --- | ---: | ---: | ---: |
| tiny2d | 2 | 1.0 | already matched in Goal5112 packet |
| bounded2d | 2 | 2.0 | 3.873 ms in retained JSON; later same-binary runs median 3.888 ms |
| bounded3d | 3 | 2.0 | 4.235 ms in retained JSON; later same-binary runs median 3.724 ms |

Additional wrapper timing on the same POD for bounded fixtures:

| Fixture | Author process wall, median of 3 | Median Running.AvgTime |
| --- | ---: | ---: |
| bounded2d | 1.079 s | 3.888 ms |
| bounded3d | 1.104 s | 3.724 ms |

The wall-clock envelope is much larger than `Running.AvgTime`, so they must not
be used as interchangeable denominators.

## RTDL Comparator Adjustment

The paper-app scripts now explicitly record:

```text
author_comparison_reference = directed_a_to_b
author_comparison_reference_value = ...
author_comparison_distance = ...
```

The symmetric Hausdorff max remains in summaries as a diagnostic:

```text
exact_reference.hausdorff
rtdl_route.hausdorff
```

It is not the author-comparison value.

## Claim Boundary

Authorized:

- bounded same-input correctness comparisons against author `HDResult`;
- phase labels distinguishing author internal `Running.AvgTime` from process
  wall-clock;
- use of directed input1-to-input2 as the author comparator.

Not authorized:

- author performance parity;
- whole-program speedup;
- replacing author `Running.AvgTime` with process wall time or vice versa;
- claiming symmetric Hausdorff is the author contract without a separate source
  audit.
