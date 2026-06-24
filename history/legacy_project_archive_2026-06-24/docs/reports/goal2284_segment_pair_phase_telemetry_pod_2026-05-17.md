# Goal2284/2285: Segment-Pair Phase Telemetry and Packed-Left Probe

Status: pod evidence recorded; external review pending.

## Purpose

Goal2283 added read-only phase telemetry after Goal2280 showed that direct-index
host exact refinement was not the right optimization. Goal2284 used that
telemetry on the RayJoin-exported 100k LSI stream. Goal2285 then tested the
natural high-performance v2 user pattern: prepare the static/right scene and
prepack the left/query segment batch once before repeated raw/count calls.

## Environment

- Commit: `ae2f56680aa122940dc4fc234be74eed644af563`
- Pod: `root@69.30.85.202 -p 22064 -i C:/Users/Lestat/.ssh/id_ed25519_rtdl_codex_current_pod`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- Query stream: `/root/goal2198_rayjoin_same_query_pod_r6/artifacts/rayjoin_lsi_gen100000_stream.json`
- Query stream producer: `rayjoin_query_exec_export_patch`
- Workload: `lsi`
- Left/query segments: `100,000`
- Right/prepared segments: `326,193`
- Exact intersections: `8,921`

## Artifacts

- Plain tuple input plus phase telemetry:
  `docs/reports/goal2284_segment_pair_phase_telemetry_pod_2026-05-17.json`
- Prepacked left/query input:
  `docs/reports/goal2285_segment_pair_packed_left_probe_pod_2026-05-17.json`

## Results

| Path | Plain Tuple Median Sec | Prepacked-Left Median Sec | Speedup |
| --- | ---: | ---: | ---: |
| Raw witness rows: `prepared.run_raw(left)` | 0.198999 | 0.009971 | 19.96x |
| Exact scalar count: `prepared.count(left)` | 0.200494 | 0.009757 | 20.55x |

The one-time left/query packing cost in Goal2285 was `0.133063` seconds. This
means manual prepacking is already useful for a single measured call on this
stream, and it is much more important when the same query batch feeds multiple
reductions or repeated measurements.

## Phase Diagnosis

Goal2284 showed that the native prepared segment-pair phases are small relative
to the plain tuple wall time:

| Phase | Raw Rows Median Sec | Count Median Sec |
| --- | ---: | ---: |
| Left upload | 0.000166 | 0.000166 |
| Candidate count pass | 0.000590 | 0.000560 |
| Candidate write pass | 0.000498 | 0.000491 |
| Candidate download | 0.000096 | 0.000092 |
| Exact refine | 0.010875 | 0.010752 |

The repeated-call wall time with tuple input was about `0.20` seconds, while
the measured native phases sum to about `0.012` seconds. The missing time is the
Python boundary work, primarily repacking the 100k left/query segments on every
call.

Goal2285 validates the fix available to a v2 user today: call
`rtdsl.optix_runtime.pack_segments(records=left_records)` once and pass that
packed object to `prepared.run_raw(...)` or `prepared.count(...)`.

## Interpretation

This is a strong v2 programming-model lesson:

- prepare static/right geometry;
- prepack reusable left/query geometry;
- then run raw/count/reduction calls over packed inputs.

For sparse LSI on this stream, the next native optimization is not another host
metadata lookup change. Once packing is removed from the repeated-call path, the
largest measured native phase is exact refinement at about `0.008-0.011`
seconds. That points future work toward generic device-resident or
partner-continuation reductions if we need to remove the remaining host exact
refinement.

## Claim Boundary

Allowed claim:

On the recorded RTX A5000 pod and RayJoin-exported 100k LSI stream, reusing a
prepacked left/query segment batch improves repeated prepared segment-pair raw
row and scalar-count calls by about `20x` versus passing the tuple records to
each call.

Not allowed:

- whole RayJoin application speedup;
- RayJoin paper reproduction;
- RTDL beats RayJoin;
- broad RT-core speedup;
- true zero-copy;
- claim that all workloads get a 20x gain from prepacking.
