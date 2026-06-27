# Phoenix V3 M11 Spatial Segment-Intersection Runner Focused POD A/B

Status: `m11_focused_pod_ab_complete_productized_coverage_pass_performance_fail`

This was the one focused POD A/B authorized by the M10 2-AI consensus. It does
not authorize release, public speedup wording, broad V3-over-V2 wording, or
all-app POD spend.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
full_all_app_pod_spend_authorized: false
```

## Protocol

- POD: `root@213.173.108.14 -p 11592`
- Key used:
  `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- Remote tree: `/root/rtdl_v3_rebuild_20260620/current`
- Dataset: `derived/authored_lsi_crossing_tiled_x2048`
- Workload: `lsi`
- Old route: `prepared_optix_left_id_dense_count`
- New route: `prepared_execution_segment_intersection_topology_stream`
- Repeat/warmup: `--repeat 5 --warmup 1`
- Outer samples: `9` per route
- Rows: `--no-rows`

Evidence:
`docs/rebuild/v3/evidence/phoenix_v3_spatial_lsi_segment_runner_m10_focused_pod_ab_20260622`

## Result

| Metric | Value |
| --- | ---: |
| Old hot median sec | `0.00012440979480743408` |
| New inner hot median sec | `0.00013191252946853638` |
| New runner-inclusive median sec | `0.00020245462656021118` |
| Old/new inner hot speedup | `0.9431234114656877x` |
| Old hot/new runner-inclusive speedup | `0.6145070474367939x` |
| New runner-inclusive slowdown vs old hot | `1.62732063720206x` |

Both routes returned count `2048`.

## Metadata Gates

All passed:

- old route returncode zero
- new route returncode zero
- new route `productized_execution_path == prepared_execution_session_runner`
- new route `runtime_trunk_executes_end_to_end`
- new route validation passed
- internal RTDL device residency present
- no hot-path host materialization flag
- topology-stream prepared-handle contract present
- M3 phase-table contract present
- M3 phase table complete

## Interpretation

M11 is a productized-runner coverage success, but a performance failure.

The new route finally proves the Spatial/RayJoin LSI family can execute through
the productized V3 runtime trunk with clean metadata. That matters for the V3
architecture.

It does not make this row faster. On the inner hot metric, the new route is
about `0.943x` of the old route, a roughly `7.5` microsecond regression. That
delta is smaller than the original M9 `15.4` microsecond frozen-row regression,
so it should not be over-interpreted as a major algorithmic loss.

The runner-inclusive median is the more serious warning: the productized route
is `1.627x` slower than the old hot metric. That is a real current cost of the
generic runner/wrapper path unless reduced or amortized.

## Decision

Do not count M11 as a speed win. Do not run all-app from this result. Do not
claim Phoenix V3 is better because this route is now productized.

The useful next decision is whether to:

- reduce generic prepared-execution runner overhead, especially metadata and
  per-repeat wrapper cost, or
- retarget the next Set-A family to a route where productized-runner overhead
  amortizes across more useful work.

That decision needs review before another POD spend.

## Goal-Level Decision Audit

Decision: classify M11 as productized-runner coverage pass but performance
fail.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   The foolish action would be to call clean metadata a performance success or
   hide the runner-inclusive slowdown.
3. Was there another path?
   Yes: keep tuning this route immediately. That would be premature without
   review because the focused POD shows the current local productized wrapper
   adds overhead.
4. Can I now try a different path?
   Yes: record the negative result, seek review, and decide whether to optimize
   generic runner overhead or retarget a different Set-A family.
