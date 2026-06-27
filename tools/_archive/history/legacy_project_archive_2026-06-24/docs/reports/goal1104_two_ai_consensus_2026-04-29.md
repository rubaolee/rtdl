# Goal1104 Two-AI Consensus

Date: 2026-04-29

## Scope

Goal1104 records the safe local Barnes-Hut Embree validation baseline and hardens source-commit stamping after a stale local `.rtdl_source_commit` file was detected.

## Consensus

| Reviewer | Verdict | Evidence |
| --- | --- | --- |
| Gemini | ACCEPT | `docs/reports/goal1104_gemini_review_2026-04-29.md` |
| Codex | ACCEPT | Barnes-Hut baseline artifact, Goal1102 intake, source-commit fallback patch, focused tests |

Claude review was attempted first but failed because the org monthly usage limit was reached. Gemini completed the external-style review and wrote the review file.

## Agreed Findings

| Check | Result |
| --- | --- |
| Barnes-Hut Embree validation artifact | `matches_oracle: true`, `query_count: 4096`, `node_count: 65536`, median native query `0.00486608303617686` sec |
| Source commit | artifact stamped with current `HEAD`: `c500a63fe36efaeac994159e8c37f72797398d85` |
| Goal1102 intake | `ok_count: 1`, `missing_count: 3`, `blocked_count: 0`, `overall_status: waiting_for_baseline_artifacts` |
| Public speedup claim | not authorized |

Claude noted a non-blocking test gap for the git-unavailable archive fallback path. Codex added `test_source_commit_falls_back_to_source_file_when_git_is_unavailable` to cover that path.

## Source-Commit Fix

The source-commit lookup order is now:

1. `RTDL_SOURCE_COMMIT`;
2. `git rev-parse HEAD`;
3. `.rtdl_source_commit` fallback for archive-style pod checkouts without `.git`.

This avoids stale local untracked source files while preserving pod archive fallback behavior.

## Verification

Commands run:

```bash
RTDL_SOURCE_COMMIT=$(git rev-parse HEAD) PYTHONPATH=src:. python3 scripts/goal1101_current_contract_non_optix_baseline_profiler.py --scenario barnes_hut_node_coverage --backend embree --body-count 4096 --iterations 3 --radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --output-json docs/reports/goal1101_current_contract_non_optix_baselines/barnes_hut_depth8_4096_embree_validation_baseline.json
PYTHONPATH=src:. python3 scripts/goal1102_current_contract_baseline_intake.py
PYTHONPATH=src:. python3 -m unittest tests.goal887_prepared_decision_phase_profiler_test tests.goal1101_current_contract_non_optix_baseline_profiler_test tests.goal1102_current_contract_baseline_intake_test
bash -n scripts/goal1084_facility_recentered_rtx_pod_packet_runner.sh scripts/goal1093_barnes_hut_20m_contract_runner.sh scripts/goal1101_current_contract_non_optix_baseline_runner.sh
```

Results:

- Barnes-Hut baseline run: completed;
- Goal1102 intake: `ok_count: 1`, `missing_count: 3`;
- Focused tests: 17 tests, OK;
- Shell syntax: OK.

## Boundary

Goal1104 does not authorize public RTX speedup claims. The baseline set remains incomplete; the remaining three rows still require execution and intake before any baseline-review or public-wording gate can proceed.
