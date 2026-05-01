# Goal978 Two-AI Consensus

Status: `ACCEPT`

Goal978 is closed for RTX speedup-claim candidate auditing.

## Codex Verdict

Accept. Goal978 audits all `17` post-Goal971 RTX rows after Goal836 reached `50 / 50` valid baseline artifacts. After Goal979 repaired zero CPU oracle timings, Goal981 repaired the graph Embree correctness issue found by Goal980, and Goal982 added a same-scale Embree graph timing baseline, it separates rows into claim-review candidates, internal-only rows, and rejected current public-speedup rows, while authorizing `0` public RTX speedup claims.

## Claude Verdict

Claude returned `ACCEPT` in `/Users/rl2025/rtdl_python_only/docs/reports/goal978_claude_review_2026-04-26.md`.

Claude verified:

- all ratio calculations are arithmetically correct
- the `source_backend == "optix"` self-comparison exclusion works
- the initial pre-Goal979 version conservatively demoted `hausdorff_distance`, `ann_candidate_search`, and `barnes_hut_force_app` because required CPU oracle timing was missing or zero
- the initial pre-Goal980 graph state correctly remained blocked rather than claimable
- all public speedup authorization fields remain `False`

Goal979 then repaired the zero CPU oracle timings and Goal978 was regenerated. The post-repair state is stricter: `hausdorff_distance` and `barnes_hut_force_app` are rejected for current public speedup claims because CPU oracle timing is faster than the RTX phase, while `ann_candidate_search` becomes a candidate for separate 2-AI public-claim review.

Goal980 then found CPU/Embree graph summary mismatches. Goal981 repaired the native Embree traversal candidate bounds and Goal980 was regenerated with status `ok`. Goal982 then added a same-scale Embree graph timing baseline at `copies=20000`, causing the graph row to be classified as `reject_current_public_speedup_claim` because the current OptiX phase is slower than Embree.

## Final State

- rows audited: `17`
- candidate rows for separate 2-AI public-claim review: `7`
- internal-only rows: `1`
- timing-repair rows: `0`
- graph-correctness-repair rows: `0`
- rejected current public-speedup rows: `9`
- public RTX speedup claims authorized: `0`

The next work is a separate claim-review goal for the seven candidate rows using larger-scale repeat evidence where needed, or performance work on rejected rows before any future claim review.
