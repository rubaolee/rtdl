# Goal2280: Direct-Index Refinement Negative A/B Probe

Status: negative evidence accepted by Codex; Goal2279 implementation reverted.

## Purpose

Goal2279 tried to optimize the prepared segment-pair intersection path by
threading direct primitive indices from the OptiX candidate row into the host
exact-refinement stage. The hypothesis was that sparse RayJoin-exported LSI
would improve by avoiding host `id -> segment` lookup work after Goal2275 had
already cached the prepared right-side lookup.

The first implementation widened the candidate row and immediately showed why
that was risky. A compact-record revision kept the candidate row at 16 bytes,
but a same-pod A/B run still did not justify carrying the change.

## Same-Pod A/B Setup

- Pod: `root@69.30.85.202 -p 22064 -i C:/Users/Lestat/.ssh/id_ed25519_rtdl_codex_current_pod`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- Query stream: `/root/goal2198_rayjoin_same_query_pod_r6/artifacts/rayjoin_lsi_gen100000_stream.json`
- Query stream producer: `rayjoin_query_exec_export_patch`
- Workload: `lsi`
- Left/query segments: `100,000`
- Right/prepared segments: `326,193`
- Exact intersections: `8,921`
- Warmups/repeats: `2` warmups and `9` measured repeats per path.
- Canonical paired summary:
  `docs/reports/goal2280_direct_index_ab_same_pod_summary_2026-05-17.json`

## Compared Commits

| Role | Commit | Meaning |
| --- | --- | --- |
| Baseline | `5c41ade112fb7ebbcdd6ed593eea96eb806db75f` | Goal2275 cached prepared right lookup |
| Candidate | `2a63e71dcb31f7227673d2055b749757aa5e8f9b` | Goal2279 direct index plus compact candidate row |

## Results

| Path | Baseline Median Sec | Candidate Median Sec | Same-Pod Speedup |
| --- | ---: | ---: | ---: |
| Raw witness rows: `prepared.run_raw(left)` | 0.173942 | 0.184194 | 0.944x |
| Exact scalar count: `prepared.count(left)` | 0.167111 | 0.166387 | 1.004x |

Parity held in both runs: raw row count and scalar count were both `8,921`.

## Decision

The direct-index refinement is not accepted. The raw witness-row path regressed
on the same pod, and the scalar-count path was effectively neutral. The paired
summary's `same_pod_speedups` values are the canonical comparison for this
decision; per-artifact `improvement_vs_goal2276` fields are legacy helper
fields from the probe script and are not the same-pod A/B authority. The
implementation was reverted so `main` keeps the previously accepted Goal2275
cached-lookup behavior.

This result narrows the next optimization target. The remaining sparse-LSI cost
is not primarily the prepared right-side lookup or the host lookup used during
exact refinement. Future work should prioritize a generic device-resident or
partner-continuation path for segment-pair predicate/count, so the runtime can
avoid candidate copyback plus host exact refinement when the user only needs a
downstream reduction.

## Claim Boundary

Allowed claim:

On the recorded RTX A5000 pod and RayJoin-exported 100k LSI stream,
direct-index host exact refinement was tested and rejected because it did not
improve the accepted Goal2275 cached-lookup baseline.

Not allowed:

- direct-index speedup claim;
- whole RayJoin application speedup;
- RayJoin paper reproduction;
- RTDL beats RayJoin;
- broad RT-core speedup;
- true zero-copy or pure device-resident continuation.
