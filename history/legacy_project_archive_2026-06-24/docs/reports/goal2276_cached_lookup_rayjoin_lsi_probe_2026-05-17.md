# Goal2276: Cached Lookup RayJoin LSI Pod Probe

Status: accepted local evidence pending external review.

## Purpose

Goal2275 cached the right-side `id -> segment` lookup inside the prepared
segment-pair handle. Goal2276 measures that change on the same RayJoin-exported
100,000-query LSI stream used by Goal2273.

## Environment

- Commit: `5c41ade112fb7ebbcdd6ed593eea96eb806db75f`
- Baseline implementation commit: `dffabc1317f382dcb19cd3ea30087692a0b69e48`
- Pod: `root@69.30.85.202 -p 22064 -i C:/Users/Lestat/.ssh/id_ed25519_rtdl_codex_current_pod`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- Query stream producer: `rayjoin_query_exec_export_patch`
- Workload: `lsi`
- Left/query segments: `100,000`
- Right/prepared segments: `326,193`
- Exact intersections: `8,921`

## Results

| Path | Goal2273 Median Sec | Goal2276 Median Sec | Speedup |
| --- | ---: | ---: | ---: |
| Raw witness rows: `prepared.run_raw(left)` | 0.181889 | 0.165026 | 1.102x |
| Exact scalar count: `prepared.count(left)` | 0.185313 | 0.159957 | 1.159x |

Within Goal2276:

- Count / raw rows: `0.969x`
- Raw rows / count: `1.032x`
- Parity: `true`

## Interpretation

The cached right lookup gives a modest but real improvement on the sparse
RayJoin-exported LSI stream. This confirms that a generic prepared-scene cache
was worth doing. It does not fully solve the LSI performance gap: most of the
time remains in traversal, candidate transfer, left-side lookup construction,
and exact refinement.

The result changes the Goal2273 diagnosis slightly:

- count-only by itself was not enough,
- caching prepared right-side metadata helps both raw rows and scalar count,
- the next larger step is still a generic device/partner continuation for
  segment-pair predicate/count, not an app-specific RayJoin engine path.

## Claim Boundary

Allowed claim:

On the recorded RTX A5000 pod and RayJoin-exported 100k LSI stream, caching the
prepared right-side segment lookup improves the exact prepared segment-pair raw
row path by about `1.10x` and the scalar-count path by about `1.16x` versus the
Goal2273 baseline implementation.

Not allowed:

- whole RayJoin application speedup,
- RayJoin paper reproduction,
- RTDL beats RayJoin,
- broad RT-core speedup,
- true zero-copy or pure device-resident continuation.

