# Goal2472 Codex/Gemini Consensus - Self-Range Blocked Candidate Pod Evidence

Date: 2026-05-21

Consensus participants:

- Codex implementation and pod validation.
- Gemini review:
  `docs/reviews/goal2472_gemini_review_self_range_blocked_candidate_pod_2026-05-21.md`.

## Decision

Goal2472 is accepted as a correct generic runtime scaffold, but rejected as a
performance optimization to promote.

The new OptiX symbol is app-independent and useful:

```text
rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs
```

It lets callers execute prepared fixed-radius grouped union over explicit
contiguous self-query ranges without host query repacking. The ABI and metadata
use generic fixed-radius/grouped-union vocabulary and do not add DBSCAN-native
engine semantics.

## Evidence

Pod endpoint:

```text
ssh root@69.30.85.171 -p 22118 -i /Users/rl2025/.ssh/id_ed25519_rtdl_codex
```

Environment:

```text
host: dd76e004260f
gpu: NVIDIA RTX A5000, driver 570.211.01
cuda nvcc: Build cuda_12.8.r12.8/compiler.35583870_0
OptiX headers: NVIDIA/optix-dev v8.0.0
```

Focused Goal2457-2472 tests passed on the pod: 50 tests OK.

Tail-median grouped-stream column-signature timings:

| points | mode | block size | total median sec | total / unblocked | grouped native median sec | native / unblocked | signatures match |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 32,768 | unblocked | - | 0.043300 | 1.00x | 0.031052 | 1.00x | true |
| 32,768 | blocked | 8,192 | 0.103427 | 2.39x | 0.086930 | 2.80x | true |
| 32,768 | blocked | 16,384 | 0.065727 | 1.52x | 0.049719 | 1.60x | true |
| 32,768 | blocked | 32,768 | 0.045744 | 1.06x | 0.030972 | 1.00x | true |
| 65,536 | unblocked | - | 0.110211 | 1.00x | 0.082476 | 1.00x | true |
| 65,536 | blocked | 8,192 | 0.312898 | 2.84x | 0.279092 | 3.38x | true |
| 65,536 | blocked | 16,384 | 0.182378 | 1.65x | 0.150733 | 1.83x | true |
| 65,536 | blocked | 32,768 | 0.120403 | 1.09x | 0.089654 | 1.09x | true |

Artifacts:

```text
docs/reports/goal2472_grouped_stream_range_pod_unblocked/
docs/reports/goal2472_grouped_stream_range_pod_blocked_q8192/
docs/reports/goal2472_grouped_stream_range_pod_blocked_q16384/
docs/reports/goal2472_grouped_stream_range_pod_blocked_q32768/
```

## Agreed Interpretation

The pod data is consistent: launch-level query chunking adds overhead and does
not reduce enough global grouped-union cost to win. Smaller blocks are much
slower; the largest tested block is close but still slower end-to-end, and it
does not justify promotion.

Gemini explicitly accepted the conclusion that the range symbol is a correct
generic scaffold while explicit query-range blocking should not be promoted as
a performance optimization. Gemini found no blocking issues in ABI naming,
metadata, app-independent boundary, or benchmark evidence.

## Next Step

Use Goal2471 atomic telemetry to design a true segmented/proposal-reduction
grouped continuation inside a launch. The next candidate should reduce global
parent atomic attempts before applying global atomics, with fail-closed
fallback. Do not spend more time trying to optimize this workload by adding
more launch-level query chunks.

Performance claim status: unauthorized. This consensus only authorizes the
engineering direction above.
