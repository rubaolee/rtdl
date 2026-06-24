# Phoenix V3 M13 Spatial Segment-Intersection Runner Focused POD Rerun

Status: `m13_focused_pod_ab_complete_overhead_improved_but_speed_fail`

This was the single guarded focused POD rerun authorized after M12. It repeats
the same Spatial LSI A/B from M11 after the generic runner hot-repeat /
finalize-once overhead reduction.

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
`docs/rebuild/v3/evidence/phoenix_v3_spatial_lsi_segment_runner_m13_focused_pod_ab_20260622`

## Result

| Metric | M11 | M13 |
| --- | ---: | ---: |
| Old hot median sec | `0.00012440979480743408` | `0.0001227855682373047` |
| New inner hot median sec | `0.00013191252946853638` | `0.00012449920177459717` |
| New runner-inclusive median sec | `0.00020245462656021118` | `0.00015626102685928345` |
| Old/new inner hot speedup | `0.9431234114656877x` | `0.9862357869539198x` |
| Old hot/new runner-inclusive speedup | `0.6145070474367939x` | `0.7857721832832689x` |

M13 improves the productized runner median by `1.2956181757497736x` versus
M11, but the productized runner is still slower than the old route on the
runner-inclusive metric.

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
- `measured_run_prepared_override_used`
- `measured_output_finalized_once`
- `per_repeat_output_finalization_avoided`

## Interpretation

M13 proves the M12 overhead reduction worked mechanically and materially: the
runner-inclusive median improved from about `202.5us` to `156.3us`.

M13 still does not produce a speed win. The new route is near parity on the
inner hot metric, but the productized runner remains about `1.27x` slower than
the old hot route when runner overhead is included.

This means Spatial LSI remains productized-runner coverage, not speed coverage.
Do not run all-app from this result and do not claim Phoenix V3 is faster from
this row.

## Next Decision

Review should decide whether to:

- do one more local-only generic runner-overhead pass if a concrete remaining
  source is identified, or
- close Spatial LSI as coverage-only and retarget the next Set-A family.

No further POD is authorized by this report.

## Goal-Level Decision Audit

Decision: Classify M13 as overhead-improved but still speed-fail.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   The foolish action would be to treat the `1.296x` M13-vs-M11 runner
   improvement as a V3 speed win against V2 or the old route.
3. Was there another path?
   Yes: keep running POD until noise helps. That would violate the focused-rerun
   guardrail.
4. Can I now try a different path?
   Yes: seek review and either do a local-only second overhead pass if
   justified or retarget without counting this as speed coverage.
