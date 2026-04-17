# Goal 470: v0.7 Pre-Release Full Test, Doc Refresh, And Audit

Date: 2026-04-16
Author: Codex
Status: Accepted with 2-AI consensus

## Verdict

`PASS` with 2-AI consensus:

- Codex implementation/test/doc/audit review
- Gemini Flash external-style review:
  `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal470_external_review_2026-04-16.md`
- Claude test-review-audit review:
  `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal470_claude_test_review_audit_2026-04-16.md`

Goal 470 adds the current full-test, documentation-refresh, and audit evidence
for the bounded `v0.7` DB line after Goal 469. No staging, commit, tag, push,
merge, or release action was performed.

Claude was unavailable before 3pm per user note, so Gemini Flash was used for
the first external review. After Claude became available, Claude performed the
requested independent test/review/audit pass and also returned `ACCEPT`.

## Local Full Test Evidence

Command run from `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`:

```text
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*test.py' -v
```

Initial result:

- `Ran 941 tests`
- `FAILED (errors=1, skipped=104)`

The one failure was not workload correctness. It was a test-harness issue in
Goal 429: missing local OptiX raised `FileNotFoundError` during `setUpClass`
instead of becoming an optional-backend skip on macOS.

Fix:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal429_v0_7_rt_db_cross_engine_postgresql_correctness_gate_test.py`

Corrected full-discovery result:

```text
Ran 941 tests in 276.632s
OK (skipped=105)
```

Transcript:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal470_local_full_unittest_discovery_after_fix_2026-04-16.txt`

## Linux Focused Pre-Release Evidence

Current worktree synced to:

- `/home/lestat/work/rtdl_goal470_pre_release`

Linux host:

- `lestat-lx1`
- Python 3.12.3
- PostgreSQL 16.13
- PostgreSQL readiness: accepting connections
- GPU: NVIDIA GeForce GTX 1070, driver 580.126.09

Backend build/probe:

```text
Embree 4.3.0
OptiX [9, 0, 0]
Vulkan [0, 1, 0]
```

Focused v0.7 DB/PostgreSQL/native command covered:

- PostgreSQL correctness tests
- cross-engine PostgreSQL correctness gate
- phase-split/performance-contract tests
- Embree/OptiX/Vulkan native prepared dataset tests
- Embree/OptiX/Vulkan columnar transfer tests
- high-level prepared DB columnar default tests
- app and kernel DB demos
- external report response regression
- Goal 469 attack-gap closure tests
- imported 105-test DB attack suite

Result:

```text
Ran 155 tests in 8.776s
OK
```

Transcript:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal470_linux_focused_pre_release_test_2026-04-16.txt`

## Documentation Refresh

Release-facing docs refreshed through Goal 470:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/release_statement.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/support_matrix.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/audit_report.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_7/tag_preparation.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/history/goals/v0_7_goal_sequence_2026-04-15.md`

The refreshed docs now include:

- Goal 469 external DB attack-report response
- Goal 470 local full discovery and Linux focused test evidence
- explicit no-DBMS boundary
- explicit no-tag/no-merge/no-release hold
- Linux remains the canonical PostgreSQL/GPU validation platform
- GTX 1070 no-RT-core hardware caveat remains in force

## Mechanical Audit

Script:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal470_pre_release_doc_audit.py`

The script checks:

- required release-facing docs exist
- required Goal 469/470 artifacts exist
- release-facing docs include required Goal 469/470 and honesty-boundary text
- release-facing doc links resolve
- local and Linux transcript summaries match expected pass conditions
- staging and release authorization are false

Audit artifact:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal470_pre_release_doc_audit_2026-04-16.json`

Final mechanical audit result:

```text
valid: true
```

## External Review

External-style AI review:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal470_external_review_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal470_claude_test_review_audit_2026-04-16.md`

Verdict:

```text
ACCEPT
```

## Remaining Hold Conditions

- do not stage, commit, tag, merge, push, or release without explicit user
  approval
- do not claim RT-core hardware-speedup evidence from the GTX 1070 Linux run
- do not widen `v0.7` into DBMS or arbitrary SQL claims
