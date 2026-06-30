# Goal3253: RayJoin Validated Device-Filtered PIP Current Best

Date: 2026-06-03

## Purpose

Goal3252 proved that the generic prepared point/closed-shape
`count_device_filtered(...)` path can match the exact prepared count on the
current RayJoin PIP same-slice row while avoiding candidate-row materialization,
candidate download, and host exact refinement.

Goal3253 wires that path into the RayJoin benchmark app and repeated
same-slice runner as an explicit opt-in mode:

```text
count_mode = device_filtered_validated
```

This is not a replacement for the normal exact `.count(...)` API. Each measured
PIP sample first validates against the exact prepared count, then reports only
the device-filtered count as the `prepared_query_ms` timing lane. The exact
validation timing is stored separately as `validation_exact_query_ms`.

## Code Changes

- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
  adds `count_mode="exact" | "device_filtered_validated"` for prepared OptiX
  PIP counts.
- `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py` adds
  `--rtdl-pip-count-mode device_filtered_validated`.
- The fast mode is rejected for non-PIP workloads and for PIP row mode.
- The fast mode fails closed if `count_device_filtered(...)` does not match
  exact prepared `.count(...)`.

The native engine did not receive any RayJoin-specific entry point. It still
sees generic point/closed-shape membership count contracts.

## Pod Evidence

Artifacts:

- Pod JSON:
  `docs/reports/goal3253_rayjoin_current_best_device_filtered_pip_pod_2026-06-03.json`
- Pod stdout:
  `docs/reports/goal3253_rayjoin_current_best_device_filtered_pip_pod_2026-06-03.stdout`

Environment:

```text
GPU: NVIDIA A40, driver 570.211.01
RTDL commit: 995394aeb21c0bbbb05b09a44709f4b20608d160
source_dirty: []
RTDL_OPTIX_POINT_PRIMITIVE_QUERY_HALF_EXTENT=0.25
```

The clean pod run also executed the focused contract tests before timing:

```text
Ran 18 tests in 0.010s
OK
```

## Current Same-Slice Comparison

The runner preserves the Goal3244 timing semantics: RayJoin `query_exec`
reports its own query time after its internal warmup/repeat loop, and RTDL
reports prepared query timing for the selected count lane.

| Workload | RayJoin median | RTDL median | RTDL / RayJoin | Count contract |
| --- | ---: | ---: | ---: | --- |
| LSI | `0.243203 ms` | `0.513267 ms` | `2.11x` | visible count matches: `269` vs `269` |
| PIP | `0.200462 ms` | `0.808567 ms` | `4.03x` | RTDL count `1430`; RayJoin PIP count not printed |

For PIP, the validation lane was:

```text
validation_exact_query_ms median = 0.992673 ms
```

The timed fast lane had native phase telemetry:

```text
mode = device_filtered_count
candidate_write_pass = 0
candidate_download = 0
exact_refine = 0
raw_candidate_count = emitted_count = 1430
```

## Delta From Goal3248

Goal3248's PIP median was `0.934755 ms` with the exact prepared count lane.
Goal3253's validated device-filtered PIP median is `0.808567 ms`, a `1.16x`
improvement on this bounded slice.

The RayJoin gap improved from `4.82x` to `4.03x`, but RayJoin remains much
faster on PIP. LSI is still near the improved Goal3245/Goal3248 range, but the
new same-slice rerun landed at `2.11x` slower than RayJoin rather than the
previous `1.97x`; this is treated as run-to-run variance, not a new LSI
optimization result.

## Interpretation

Goal3253 confirms that removing materialization, download, and host refine from
the PIP scalar count lane helps but does not close the RayJoin gap. The
remaining dominant cost is still the generic closed-shape traversal/predicate
pass: the median native `candidate_count_pass` stays around `0.73 ms`.

The next RayJoin PIP optimization should therefore be a stronger generic
closed-shape membership/count design, not more Python runner cleanup. Candidate
directions remain:

- tighter prepared closed-shape indexing or probe policy,
- a generic closed-shape membership count primitive that does less predicate
  work per query,
- or a broader device-resident grouped continuation if later workloads need
  per-group aggregation rather than only a scalar count.

## Boundary

Goal3253 does not authorize release, public speedup claims, broad RT-core
speedup claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.

The narrow accepted conclusion is: the validated device-filtered PIP count lane
is correct on the measured same-slice row and improves RTDL's PIP timing, but
RayJoin is still faster and the next improvement requires a deeper generic
closed-shape membership/count design.
