# Goal1105 Two-AI Consensus

Date: 2026-04-29

## Scope

Goal1105 covers Linux execution of current-contract non-OptiX baseline rows from Goal1101 and intake through Goal1102.

## Consensus

| Reviewer | Verdict | Evidence |
| --- | --- | --- |
| Gemini | ACCEPT | `docs/reports/goal1105_gemini_review_2026-04-29.md` |
| Codex | ACCEPT | Linux artifacts, Goal1102 intake, copied logs, and Goal1105 execution report |

Claude was not used for this goal because the Claude CLI reported the org monthly usage limit earlier in this session. Gemini CLI reported an ignored-log read warning for one `*.log` file because logs are ignored by repository patterns, but the raw logs are force-added with this goal and the review checked the signal-9/memory-boundary data recorded in the Goal1105 report.

## Agreed Findings

| Row | Status | Median native query |
| --- | --- | ---: |
| `barnes_hut_depth8_4096_embree_validation_baseline.json` | `matches_oracle: true` | `0.010342210996896029` s |
| `facility_recentered_2_5m_cpu_oracle_baseline.json` | `matches_oracle: true` | `8.996512651909143` s |
| `facility_recentered_2_5m_embree_baseline.json` | `matches_oracle: true` | `29.806780943996273` s |
| `barnes_hut_depth8_20m_embree_timing_baseline.json` | missing: Linux process killed by signal 9 | n/a |

Goal1102 correctly reports `ok_count: 3`, `missing_count: 1`, `blocked_count: 0`, `artifact_set_complete: false`, and `public_speedup_claim_authorized_count: 0`.

## Interpretation

The Facility CPU oracle baseline is faster than the Facility Embree baseline for this current contract. This blocks any simple Facility RTX public speedup wording against Embree without further review, and it reinforces that public wording must go through a separate gate.

The Barnes-Hut 20M Embree timing row exceeded the 16 GB Linux host memory boundary: `/usr/bin/time -v` recorded signal 9 and max RSS `15180436` KB. The row remains missing and cannot be inferred from the 4,096-body validation row.

## Verification

Commands run:

```bash
make build-embree
PYTHONPATH=src:. python3 -m unittest tests.goal1101_current_contract_non_optix_baseline_profiler_test tests.goal1102_current_contract_baseline_intake_test
PYTHONPATH=src:. python3 scripts/goal1102_current_contract_baseline_intake.py
PYTHONPATH=src:. python3 -m unittest tests.goal1101_current_contract_non_optix_baseline_profiler_test tests.goal1102_current_contract_baseline_intake_test tests.goal1103_baseline_execution_manifest_test
git diff --check -- docs/reports/goal1101_current_contract_non_optix_baselines docs/reports/linux_goal1105_logs docs/reports/goal1102_current_contract_baseline_intake_2026-04-29.json docs/reports/goal1102_current_contract_baseline_intake_2026-04-29.md docs/reports/goal1105_linux_current_contract_baseline_execution_2026-04-29.md
```

Results:

- Linux archive tests: 10 tests OK, skipped 1 git-metadata-only test;
- local focused tests: 14 tests OK;
- Goal1102 intake: `ok_count: 3`, `missing_count: 1`;
- diff check: OK.

## Boundary

Goal1105 does not authorize release, README/front-page wording, or public RTX speedup claims. The current baseline set remains incomplete because the Barnes-Hut 20M Embree timing row is missing.
