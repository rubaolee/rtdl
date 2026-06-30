# Goal2187 RayJoin Phase 0 External Consensus

Date: 2026-05-17

Status: 3-AI consensus for Goal2184 local source/protocol/sample evidence.

## Inputs

Codex implementation/report:

- `docs/reports/goal2184_rayjoin_full_reproduction_project_goal_2026-05-17.md`
- `docs/reports/goal2184_rayjoin_phase0_protocol_and_sample_evidence_2026-05-17.md`
- `docs/reports/goal2184_rayjoin_build_protocol_linux_raw_2026-05-17.txt`
- `docs/reports/goal2184_rtdl_same_rayjoin_sample_bounded_linux_2026-05-17.json`

External reviews:

- Gemini: `docs/reviews/goal2185_gemini_review_goal2184_rayjoin_phase0_2026-05-17.md`
- Claude: `docs/reviews/goal2186_claude_review_goal2184_rayjoin_phase0_2026-05-17.md`

## Verdicts

| Reviewer | Verdict | Scope |
| --- | --- | --- |
| Codex | `accept-with-boundary` | Local source/protocol/sample evidence complete; pod phase still required. |
| Gemini | `accept-with-boundary` | Accepts local evidence and authorizes next RTX pod phase, with no public performance claim. |
| Claude | `accept-with-boundary` | Accepts local evidence, flags and resolves the artifact goal-number metadata issue, and keeps paper-scale claims blocked. |

## Consensus Decision

Goal2184 is accepted for the local source/protocol/sample lane:

- real RayJoin source provenance recorded
- real RayJoin build dependency and patch state recorded
- RayJoin release/debug binaries built on local Linux
- RayJoin sample overlay run through `grid`, `lbvh`, and `rt`
- RayJoin sample LSI/PIP query runs executed through `grid`, `lbvh`, and `rt`
- RTDL v2.0 bounded same-sample PIP, LSI, and overlay-seed runs completed with
  CPU/Embree parity

The consensus is deliberately bounded. It does not authorize:

- full RayJoin paper reproduction claims
- claims that RTDL beats RayJoin
- broad RT-core speedup claims
- v2.0 release authorization
- any app-specific native RTDL engine customization

## Post-Review Correction

Claude found that the RTDL JSON artifact inherited `"goal": "2159"` from the
older runner used to execute the bounded sample cases. Codex corrected that
metadata to `"goal": "2184"` after the review. The correction did not change
dataset paths, row counts, timings, parity flags, or claim-boundary flags.

## Next Gate

The next Goal2184 phase requires an RTX pod:

1. Build RayJoin with an RTX-era SM target, not the local GTX 1070 target.
2. Run larger public or paper-aligned CDB datasets through RayJoin `grid`,
   `lbvh`, and `rt`.
3. Run RTDL v2.0 Embree/OptiX and prepared OptiX paths on the same datasets.
4. Add CUDA/CuPy spatial baselines.
5. Re-run Gemini and Claude review before any public performance conclusion.
