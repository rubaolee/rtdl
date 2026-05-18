# Goal2255: RayJoin PIP Toggle Probe

Status: diagnostic evidence recorded.

## Purpose

Goal2255 probes the current prepared closed-shape PIP path to identify which
existing runtime choices carry the speedup:

- the device-side point/closed-shape prefilter,
- the one-pass compact positive-output path,
- and the default combination used by Goal2249/2252.

This is diagnostic evidence only. It does not add a new public claim.

## Environment

- Pod SSH: `root@69.30.85.202 -p 22064`
- Commit: `949ca4f60a19b61bade10682d17a645bc07ec588`
- GPU: NVIDIA RTX A5000, driver `570.211.01`
- Query stream:
  `/root/goal2198_rayjoin_same_query_pod_r6/artifacts/rayjoin_pip_gen100000_stream.json`
- Repeats: one warmup, seven timed repeats per mode

## Results

| Mode | Environment change | Median seconds | Rows | Parity |
| --- | --- | ---: | ---: | --- |
| Default | none | 0.06666836328804493 | 8,686 | true |
| No device prefilter | `RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DISABLE_DEVICE_PREFILTER=1` | 0.5072881113737822 | 8,686 | true |
| No one-pass compact | `RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DISABLE_ONE_PASS_COMPACT=1` | 0.09405476413667202 | 8,686 | true |

Artifacts:

- `docs/reports/goal2255_rayjoin_pip_toggle_default_pod_2026-05-17.json`
- `docs/reports/goal2255_rayjoin_pip_toggle_no_prefilter_pod_2026-05-17.json`
- `docs/reports/goal2255_rayjoin_pip_toggle_no_one_pass_pod_2026-05-17.json`

## Interpretation

The default path is best. The current performance depends on two generic runtime
properties:

- device-side predicate filtering prevents a large conservative candidate stream
  from crossing back to the host;
- one-pass compact output avoids an extra count/write pass for sparse positive
  rows.

The device prefilter is the dominant control: disabling it changes the median
from `0.06666836328804493` seconds to `0.5072881113737822` seconds, about
`7.61x` slower. Disabling one-pass compact changes the median to
`0.09405476413667202` seconds, about `1.41x` slower.

## Design Lesson

The next generic runtime work should protect this shape:

- use prepared scenes for stable geometry,
- keep safe device-side predicate filtering,
- compact sparse positive rows before host-visible materialization,
- and eventually offer a device-resident output stream for partner-side
  continuation.

None of these require app-specific native names or RayJoin-specific engine
logic.

## Boundary

This diagnostic does not authorize RayJoin reproduction claims, RTDL-beats-
RayJoin claims, broad PIP claims, or v2.0 release readiness.
