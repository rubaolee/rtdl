# Goal1165 Two-AI Consensus - Local RTX App Performance Follow-Up

Date: 2026-04-30

## Verdict

ACCEPT.

Codex and Gemini agree that Goal1165 is a valid local pre-cloud optimization and documentation update following Goal1164.

## Evidence

- Local report: `docs/reports/goal1165_local_rtx_app_perf_followup_2026-04-30.md`
- Gemini review: `docs/reports/goal1165_gemini_local_rtx_app_perf_followup_review_2026-04-30.md`
- Focused tests: 23 tests passed across ANN, robot, and polygon profiler coverage.

## Consensus Points

- ANN candidate-threshold validation is correct for the authored tiled fixture when reduced to a single-tile oracle projection. This removes accidental O(copies^2) validation work from the prepared OptiX path.
- Robot prepared pose flags can use the generated fixture's analytic even/odd collision pattern for scaled validation. `--skip-validation` is acceptable for timing diagnostics because the JSON explicitly marks `validation_mode: skipped` and `matches_oracle: null`.
- Polygon Jaccard defaulting to chunk size 512 is a justified safety mitigation based on Goal1164, but arbitrary chunking remains unresolved and must not become a public speedup claim.
- The RTX pod runbook now records the driver/header/nvcc constraints discovered in Goal1164 without overclaiming NVRTC or public performance.

## Remaining Work

- Re-run ANN and robot on an RTX pod to confirm large-scale timing improvement.
- Design a real Jaccard chunk-boundary/capacity fix before treating arbitrary chunking as safe.
- Keep public speedup wording blocked until same-contract artifacts and review exist.
