# Goal2273: RayJoin LSI Segment-Pair Count Probe

Status: diagnostic pod evidence.

## Purpose

Goal2270 showed that the new prepared segment-pair exact scalar-count path helps
when witness output is dense. Goal2273 asks the application-shaped follow-up:
does the same count path materially improve the RayJoin-exported 100,000-query
LSI stream?

## Environment

- Commit: `dffabc1317f382dcb19cd3ea30087692a0b69e48`
- Pod: `root@69.30.85.202 -p 22064 -i C:/Users/Lestat/.ssh/id_ed25519_rtdl_codex_current_pod`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- Query stream: `/root/goal2198_rayjoin_same_query_pod_r6/artifacts/rayjoin_lsi_gen100000_stream.json`
- Query stream producer: `rayjoin_query_exec_export_patch`
- Workload: `lsi`
- Left/query segments: `100,000`
- Right/prepared segments: `326,193`
- Exact intersections: `8,921`

## Results

| Path | Median Sec | Count |
| --- | ---: | ---: |
| Raw witness rows: `prepared.run_raw(left)` | 0.181889 | 8,921 |
| Exact scalar count: `prepared.count(left)` | 0.185313 | 8,921 |

Ratio:

- Count / raw rows: `1.019x`
- Raw rows / count: `0.982x`

Parity: `true`.

## Interpretation

The count-only segment-pair path is not the bottleneck fix for this sparse
RayJoin-exported LSI stream. It removes final row allocation and Python row
conversion, but this stream emits only `8,921` witness rows from `100,000`
queries over `326,193` prepared right-side segments. In this shape, row output is already small;
traversal, candidate discovery, candidate copyback, and exact
refinement dominate.

This does not contradict Goal2270. Goal2270 intentionally used dense synthetic
crossing grids to isolate witness-output pressure, where the count path becomes
useful. Goal2273 shows the app-shaped sparse LSI stream needs a different next
optimization if the goal is RayJoin-like performance.

## Design Consequence

For RayJoin LSI, the next useful generic direction is not merely "count without
rows." It is a tighter generic segment-pair predicate/count path that reduces
candidate copyback and exact-refinement overhead, ideally through device-side or
partner-side continuation while keeping the engine app-agnostic.

## Claim Boundary

Allowed claim:

On the recorded RTX A5000 pod, the new exact scalar count API preserves parity
on the RayJoin-exported 100k LSI stream, but does not materially improve runtime
for that sparse stream.

Not allowed:

- whole RayJoin application speedup,
- RayJoin paper reproduction,
- RTDL beats RayJoin,
- broad RT-core speedup,
- true zero-copy or pure device-resident continuation.
