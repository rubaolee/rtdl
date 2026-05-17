# Goal2211: RayJoin Same-Query Pod Evidence 2-AI Consensus

Status: `accept-with-boundary`.

## Inputs

- Codex implementation/evidence import:
  - `docs/reports/goal2209_rayjoin_same_query_pod_evidence_2026-05-17.json`
  - `docs/reports/goal2209_rayjoin_same_query_pod_evidence_2026-05-17.md`
  - `docs/reports/goal2209_rayjoin_same_query_pod_evidence_interpretation_2026-05-17.md`
  - `tests/goal2209_rayjoin_same_query_pod_evidence_test.py`
- Independent Gemini review:
  - `docs/reviews/goal2210_gemini_review_goal2209_rayjoin_same_query_pod_evidence_2026-05-17.md`

## Consensus

Codex and Gemini agree that the Goal2209 artifact package supports these bounded findings:

- RayJoin-exported same-query streams were captured for LSI and PIP at `gen_n=100000`.
- RTDL replayed those streams with `cpu`, `embree`, and `optix` backends.
- RTDL CPU, Embree, and OptiX produced parity-matching rows against the declared native CPU reference for both workloads.
- Goal2207 fixed the previous LSI OptiX `uint32_t` capacity blocker.
- LSI OptiX is successful relative to RTDL's native CPU reference on this same-query replay.
- PIP OptiX is a weak spot: it is correct, but slower than RTDL Embree and far slower than RayJoin's specialized RT query phase.

The consensus also agrees that these claims remain unauthorized:

- RTDL beats RayJoin.
- RTDL reproduces the full RayJoin paper performance study.
- Broad RT-core speedup.
- v2.0 release readiness.

## Verdict

`accept-with-boundary`: the evidence is useful and traceable, but it is diagnostic evidence, not a public performance-win or release claim.

