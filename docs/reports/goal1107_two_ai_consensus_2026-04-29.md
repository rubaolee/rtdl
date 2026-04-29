# Goal1107 Two-AI Consensus

Date: 2026-04-29

Verdict: ACCEPT AFTER RADIUS-GUARD REMEDIATION

## Scope

Goal1107 records the Linux execution of the chunked Barnes-Hut 20M Embree timing baseline and refreshes Goal1102 baseline intake. A first radius-`10.0` artifact was superseded after detecting it did not match the Goal1093 current RTX contract. The accepted artifact uses radius `0.1`.

## Consensus

Codex verdict: ACCEPT.

Second-AI reviewer verdict: ACCEPT.

Consensus conclusion: after adding the Goal1102 radius guard and replacing the timing row with the corrected radius-`0.1` Linux artifact, the non-OptiX current-contract baseline artifact set is complete and ready for later comparison review. This does not authorize public RTX speedup claims.

## Evidence

- Linux execution report: `docs/reports/goal1107_linux_chunked_baseline_completion_2026-04-29.md`
- Second-AI review: `docs/reports/goal1107_second_ai_review_2026-04-29.md`
- Barnes-Hut 20M artifact: `docs/reports/goal1101_current_contract_non_optix_baselines/barnes_hut_depth8_20m_embree_timing_baseline.json`
- Linux timing log: `docs/reports/linux_goal1108_logs/barnes_hut_20m_chunked_embree_timing_radius_0_1.log`
- Refreshed intake: `docs/reports/goal1102_current_contract_baseline_intake_2026-04-29.md`

## Key Numbers

| Metric | Value |
| --- | ---: |
| Goal1102 OK rows | `4 / 4` |
| Public claim authorizations | `0` |
| Barnes-Hut query count | `20,000,000` |
| Barnes-Hut radius | `0.1` |
| Barnes-Hut native query median | `53.465870 s` |
| Full Linux command wall clock | `5:20.92` |
| Full Linux command max RSS | `326,732 KB` |

## Boundary

This closes the current non-OptiX baseline gap. It does not authorize public RTX speedup claims, front-page wording, release wording, or a claim that Barnes-Hut force-vector reduction is native.
