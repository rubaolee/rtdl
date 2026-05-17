# Goal2191 RayJoin Pod Evidence 3-AI Consensus

Date: 2026-05-17

Status: 3-AI consensus complete for Goal2188's bounded pod evidence.

## Scope

This consensus covers the Goal2188 evidence package:

- `docs/reports/goal2188_rayjoin_rtx_pod_build_and_bounded_rtdl_evidence_2026-05-17.md`
- `docs/reports/goal2188_rayjoin_native_pod_summary_2026-05-17.json`
- `docs/reports/goal2188_rayjoin_native_pod_sample_protocol_raw_2026-05-17.txt`
- `docs/reports/goal2188_rayjoin_native_pod_query_protocol_raw_2026-05-17.txt`
- `docs/reports/goal2188_pod_rtdl_rayjoin_pip_county512_2026-05-17.json`
- `docs/reports/goal2188_pod_rtdl_rayjoin_lsi_count512_2026-05-17.json`
- `docs/reports/goal2188_pod_rtdl_rayjoin_overlay_count512_2026-05-17.json`
- `tests/goal2188_rayjoin_rtx_pod_build_and_bounded_rtdl_evidence_test.py`

It does not cover full RayJoin paper reproduction, public RTDL-vs-RayJoin
performance claims, broad RT-core speedup claims, or v2.0 release readiness.

## Reviews

| Reviewer | File | Verdict |
| --- | --- | --- |
| Codex | `docs/reports/goal2188_rayjoin_rtx_pod_build_and_bounded_rtdl_evidence_2026-05-17.md` | `accept-with-boundary` |
| Gemini | `docs/reviews/goal2189_gemini_review_goal2188_rayjoin_pod_evidence_2026-05-17.md` | `accept-with-boundary` |
| Claude | `docs/reviews/goal2190_claude_review_goal2188_rayjoin_pod_evidence_2026-05-17.md` | `accept-with-boundary` |

## Consensus Finding

The three reviewers agree that Goal2188 is valid bounded evidence:

- RayJoin built and ran on an RTX A5000 pod.
- RayJoin `rt` paths emitted real OptiX launches.
- RayJoin sample overlay outputs diff-passed for `grid`, `lbvh`, and `rt`.
- RTDL v2.0 ran bounded RayJoin CDB-shaped PIP, LSI, and overlay-seed workloads
  with parity across the tested backend matrix.
- The RTDL native engine remained app-agnostic; no RayJoin-specific native
  engine code was added.
- The report's claim boundary is correct and should remain visible.

## Boundaries

This consensus does not authorize:

- claiming full RayJoin paper reproduction,
- claiming RTDL beats the RayJoin implementation,
- claiming broad RT-core speedup,
- claiming v2.0 release readiness,
- treating RayJoin generated-query timings and RTDL bounded CDB-slice timings
  as a direct same-contract performance comparison.

## Required Next Step For Stronger Claims

The next stronger RayJoin claim requires a same-contract reproduction lane:

1. Reconstruct the paper-aligned dataset/protocol matrix.
2. Feed RTDL the same generated query streams or equivalent query files used by
   RayJoin `query_exec`.
3. Compare exact timing boundaries: build, adaptive grouping, launch, query,
   post-processing, and output materialization.
4. Decide whether the RTDL comparison is full overlay output-chain parity or
   RT primitive/dependency-row parity.
5. Run another 3-AI review before publishing any public performance claim.

## Verdict

Goal2188 is accepted with boundary by Codex, Gemini, and Claude.

The correct public-facing status is:

> RTDL v2.0 has bounded RTX pod evidence on RayJoin CDB-shaped workloads, but
> full RayJoin paper reproduction and public RTDL-vs-RayJoin claims still
> require a same-contract reproduction run.
